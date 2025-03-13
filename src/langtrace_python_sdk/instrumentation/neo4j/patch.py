import json

from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import Span, SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, SERVICE_PROVIDERS)
from langtrace_python_sdk.utils.llm import set_span_attributes
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs


def patch_kg_pipeline_run(operation_name: str, version: str, tracer: Tracer):
    """Patch function for SimpleKGPipeline.run_async method."""
    
    async def async_traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS.get("NEO4J_GRAPHRAG", "neo4j_graphrag")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        
        # Basic attributes
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "neo4j.pipeline.type": "SimpleKGPipeline",
            **(extra_attributes if extra_attributes is not None else {}),
        }
        
        # Add input data
        if len(args) > 0:
            span_attributes["neo4j.pipeline.inputs"] = serialize_args(*args)
        if kwargs:
            span_attributes["neo4j.pipeline.kwargs"] = serialize_kwargs(**kwargs)
            
        # Extract file path or text
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        text = kwargs.get("text", args[1] if len(args) > 1 else None)
        if file_path:
            span_attributes["neo4j.pipeline.file_path"] = file_path
        if text:
            # Truncate text if too long
            span_attributes["neo4j.pipeline.text_length"] = len(text)
            
        # Add configuration data if available
        if hasattr(instance, "runner") and hasattr(instance.runner, "config"):
            config = instance.runner.config
            if config:
                span_attributes["neo4j.pipeline.from_pdf"] = getattr(config, "from_pdf", None)
                span_attributes["neo4j.pipeline.perform_entity_resolution"] = getattr(config, "perform_entity_resolution", None)

        # Create attributes object
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=f"neo4j.pipeline.{operation_name}",
            kind=SpanKind.CLIENT,
        ) as span:
            try:
                set_span_attributes(span, attributes)
                
                # Execute the original method
                result = await wrapped(*args, **kwargs)
                
                # Record result data
                if result:
                    try:
                        if hasattr(result, "to_dict"):
                            result_dict = result.to_dict()
                            span.set_attribute("neo4j.pipeline.result", json.dumps(result_dict))
                        elif hasattr(result, "model_dump"):
                            result_dict = result.model_dump()
                            span.set_attribute("neo4j.pipeline.result", json.dumps(result_dict))
                    except Exception as e:
                        span.set_attribute("neo4j.pipeline.result_error", str(e))
                
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return async_traced_method


def patch_pipeline_runner(operation_name: str, version: str, tracer: Tracer):
    """Patch function for PipelineRunner.run method."""
    
    async def async_traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS.get("NEO4J_GRAPHRAG", "neo4j_graphrag")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        
        # Basic attributes
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "neo4j.runner.type": "PipelineRunner",
            **(extra_attributes if extra_attributes is not None else {}),
        }
        
        # Add pipeline information
        if hasattr(instance, "pipeline"):
            span_attributes["neo4j.pipeline.name"] = str(instance.pipeline)
        
        # Add configuration data
        if hasattr(instance, "config") and instance.config:
            try:
                if hasattr(instance.config, "model_dump"):
                    config_dict = instance.config.model_dump()
                    span_attributes["neo4j.runner.config_type"] = config_dict.get("template_", "unknown")
            except Exception:
                pass
        
        # Add input data
        if len(args) > 0 and isinstance(args[0], dict):
            span_attributes["neo4j.runner.input_data"] = serialize_args(*args)
        if kwargs:
            span_attributes["neo4j.runner.kwargs"] = serialize_kwargs(**kwargs)

        # Create attributes object
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=f"neo4j.runner.{operation_name}",
            kind=SpanKind.CLIENT,
        ) as span:
            try:
                set_span_attributes(span, attributes)
                
                # Execute the original method
                result = await wrapped(*args, **kwargs)
                
                # Record result data
                if result:
                    try:
                        if hasattr(result, "to_dict"):
                            result_dict = result.to_dict()
                            span.set_attribute("neo4j.runner.result", json.dumps(result_dict))
                        elif hasattr(result, "model_dump"):
                            result_dict = result.model_dump()
                            span.set_attribute("neo4j.runner.result", json.dumps(result_dict))
                    except Exception as e:
                        span.set_attribute("neo4j.runner.result_error", str(e))
                
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return async_traced_method


def patch_graphrag_search(operation_name: str, version: str, tracer: Tracer):
    """Patch function for GraphRAG.search method."""
    
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS.get("NEO4J_GRAPHRAG", "neo4j_graphrag")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        
        # Basic attributes
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "neo4j.graphrag.operation": operation_name,
            **(extra_attributes if extra_attributes is not None else {}),
        }
        
        # Extract query text
        query_text = kwargs.get("query_text", args[0] if len(args) > 0 else None)
        if query_text:
            span_attributes["neo4j.graphrag.query_text"] = query_text
        
        # Add retriever configuration
        retriever_config = kwargs.get("retriever_config", None)
        if retriever_config:
            span_attributes["neo4j.graphrag.retriever_config"] = json.dumps(retriever_config)
        
        # Add retriever type
        if hasattr(instance, "retriever"):
            span_attributes["neo4j.graphrag.retriever_type"] = instance.retriever.__class__.__name__
        
        # Add LLM type
        if hasattr(instance, "llm"):
            span_attributes["neo4j.graphrag.llm_type"] = instance.llm.__class__.__name__

        # Create attributes object
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=f"neo4j.graphrag.{operation_name}",
            kind=SpanKind.CLIENT,
        ) as span:
            try:
                set_span_attributes(span, attributes)
                
                # Execute the original method
                result = wrapped(*args, **kwargs)
                
                # Record result data
                if result and hasattr(result, "answer"):
                    span.set_attribute("neo4j.graphrag.answer", result.answer)
                    
                    # Record context info if available
                    if hasattr(result, "retriever_result") and result.retriever_result:
                        try:
                            retriever_items = len(result.retriever_result.items)
                            span.set_attribute("neo4j.graphrag.context_items", retriever_items)
                        except Exception:
                            pass
                
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def patch_retriever_search(operation_name: str, version: str, tracer: Tracer):
    """Patch function for Retriever.search methods."""
    
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS.get("NEO4J_GRAPHRAG", "neo4j_graphrag")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        
        # Basic attributes
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "neo4j.retriever.operation": operation_name,
            "neo4j.retriever.type": instance.__class__.__name__,
            **(extra_attributes if extra_attributes is not None else {}),
        }
        
        # Extract query text
        query_text = kwargs.get("query_text", args[0] if len(args) > 0 else None)
        if query_text:
            span_attributes["neo4j.retriever.query_text"] = query_text
        
        # Add retriever-specific attributes based on type
        if hasattr(instance, "__class__") and hasattr(instance.__class__, "__name__"):
            retriever_type = instance.__class__.__name__
            
            # Add index name for vector retriever
            if retriever_type == "VectorRetriever" and hasattr(instance, "index_name"):
                span_attributes["neo4j.vector_retriever.index_name"] = instance.index_name
                
            # Add cypher query for KG retriever if available
            if retriever_type == "KnowledgeGraphRetriever" and hasattr(instance, "cypher_query"):
                span_attributes["neo4j.kg_retriever.cypher_query"] = instance.cypher_query
        
        # Add other parameters
        for param in ["top_k", "similarity_threshold"]:
            if param in kwargs:
                span_attributes[f"neo4j.retriever.{param}"] = kwargs[param]
            elif hasattr(instance, param):
                span_attributes[f"neo4j.retriever.{param}"] = getattr(instance, param)

        # Create attributes object
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=f"neo4j.retriever.{operation_name}",
            kind=SpanKind.CLIENT,
        ) as span:
            try:
                set_span_attributes(span, attributes)
                
                # Execute the original method
                result = wrapped(*args, **kwargs)
                
                # Record result data
                if result:
                    # Record number of items retrieved
                    if hasattr(result, "items") and isinstance(result.items, list):
                        span.set_attribute("neo4j.retriever.items_count", len(result.items))
                        
                        # Record first few item IDs for debugging
                        try:
                            item_ids = [item.id for item in result.items[:5] if hasattr(item, "id")]
                            if item_ids:
                                span.set_attribute("neo4j.retriever.item_ids", json.dumps(item_ids))
                        except Exception:
                            pass
                
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method
