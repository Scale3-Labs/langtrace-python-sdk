import json
import inspect
from typing import Collection
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry import trace
from wrapt import wrap_function_wrapper as _W
from importlib_metadata import version as v
from .patch import patch_graphrag_search, patch_kg_pipeline_run, \
patch_kg_pipeline_run, patch_retriever_search, patch_pipeline_runner

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.utils.llm import set_span_attributes, get_span_name
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs
from langtrace.trace_attributes import FrameworkSpanAttributes


class Neo4jGraphRAGInstrumentation(BaseInstrumentor):
    """Instrumentor for Neo4j GraphRAG components."""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["neo4j-graphrag>=1.0.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = trace.get_tracer(__name__, "", tracer_provider)
        
        try:
            # Get versions - handle potential import errors gracefully
            try:
                graphrag_version = v("neo4j_graphrag")
            except Exception:
                graphrag_version = "unknown"
                
            # Instrument SimpleKGPipeline
            _W(
                "neo4j_graphrag.pipelines.simple",
                "SimpleKGPipeline.run_async",
                patch_kg_pipeline_run("run_async", graphrag_version, tracer),
            )
            
            # Instrument PipelineRunner
            _W(
                "neo4j_graphrag.pipelines.runner",
                "PipelineRunner.run",
                patch_pipeline_runner("run", graphrag_version, tracer),
            )
            
            # Instrument GraphRAG
            _W(
                "neo4j_graphrag.generation.graphrag",
                "GraphRAG.search",
                patch_graphrag_search("search", graphrag_version, tracer),
            )
            
            # Instrument retrievers
            _W(
                "neo4j_graphrag.retrievers.vector",
                "VectorRetriever.search",
                patch_retriever_search("vector_search", graphrag_version, tracer),
            )
            _W(
                "neo4j_graphrag.retrievers.knowledge_graph",
                "KnowledgeGraphRetriever.search",
                patch_retriever_search("kg_search", graphrag_version, tracer),
            )
            
        except Exception as e:
            # Log the error but don't crash
            print(f"Failed to instrument Neo4j GraphRAG: {e}")

    def _uninstrument(self, **kwargs):
        pass