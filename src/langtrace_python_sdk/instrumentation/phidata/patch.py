import json
from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import Span, SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode
from typing import Dict, Any, Optional

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import get_span_name, set_span_attributes
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs

def _extract_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to extract and format metrics"""
    formatted_metrics = {}
    
    # Extract basic metrics
    for key in ['time', 'time_to_first_token', 'input_tokens', 'output_tokens', 
                'prompt_tokens', 'completion_tokens', 'total_tokens']:
        if key in metrics:
            formatted_metrics[key] = metrics[key]
    
    # Extract nested metric details if present
    if 'prompt_tokens_details' in metrics:
        formatted_metrics['prompt_tokens_details'] = metrics['prompt_tokens_details']
    if 'completion_tokens_details' in metrics:
        formatted_metrics['completion_tokens_details'] = metrics['completion_tokens_details']
    if 'tool_call_times' in metrics:
        formatted_metrics['tool_call_times'] = metrics['tool_call_times']
        
    return formatted_metrics

def patch_memory(operation_name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["PHIDATA"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        span_attributes.update({
            "phidata.memory.type": type(instance).__name__,
            "phidata.memory.create_session_summary": str(instance.create_session_summary),
            "phidata.memory.create_user_memories": str(instance.create_user_memories),
            "phidata.memory.retrieval": str(instance.retrieval)
        })

        inputs = {}
        if len(args) > 0:
            inputs["args"] = serialize_args(*args)
        if len(kwargs) > 0:
            inputs["kwargs"] = serialize_kwargs(**kwargs)
        span_attributes["phidata.memory.inputs"] = json.dumps(inputs)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                result = wrapped(*args, **kwargs)

                if result is not None:
                    set_span_attribute(span, "phidata.memory.output", str(result))

                if instance.summary is not None:
                    set_span_attribute(span, "phidata.memory.summary", str(instance.summary))
                if instance.memories is not None:
                    set_span_attribute(span, "phidata.memory.memories_count", str(len(instance.memories)))
                
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method

def patch_agent(operation_name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["PHIDATA"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                PhiDataSpanAttributes(span=span, instance=instance)
                result_generator = wrapped(*args, **kwargs)

                accumulated_content = ""
                current_tool_call = None
                response_metadata = None
                seen_tool_calls = set()

                try:
                    for response in result_generator:
                        if not hasattr(response, 'model_dump'):
                            yield response
                            continue

                        if not response_metadata:
                            response_metadata = {
                                "run_id": response.run_id,
                                "agent_id": response.agent_id,
                                "session_id": response.session_id,
                                "model": response.model,
                                "content_type": response.content_type,
                            }
                            for key, value in response_metadata.items():
                                if value is not None:
                                    set_span_attribute(span, f"phidata.agent.{key}", str(value))

                        if response.content:
                            accumulated_content += response.content
                            set_span_attribute(span, "phidata.agent.response", accumulated_content)

                        if response.messages:
                            for msg in response.messages:
                                if msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        tool_id = tool_call.get('id')
                                        if tool_id and tool_id not in seen_tool_calls:
                                            seen_tool_calls.add(tool_id)
                                            tool_info = {
                                                'id': tool_id,
                                                'name': tool_call.get('function', {}).get('name'),
                                                'arguments': tool_call.get('function', {}).get('arguments'),
                                                'start_time': msg.created_at,
                                            }
                                            current_tool_call = tool_info
                                            set_span_attribute(span, f"phidata.agent.tool_call.{tool_id}", json.dumps(tool_info))

                                if msg.metrics:
                                    metrics = _extract_metrics(msg.metrics)
                                    role_prefix = f"phidata.agent.metrics.{msg.role}"
                                    for key, value in metrics.items():
                                        set_span_attribute(span, f"{role_prefix}.{key}", str(value))

                        if response.tools:
                            for tool in response.tools:
                                tool_id = tool.get('tool_call_id')
                                if tool_id and current_tool_call and current_tool_call['id'] == tool_id:
                                    tool_result = {
                                        **current_tool_call,
                                        'result': tool.get('content'),
                                        'error': tool.get('tool_call_error'),
                                        'end_time': tool.get('created_at'),
                                        'metrics': tool.get('metrics'),
                                    }
                                    set_span_attribute(span, f"phidata.agent.tool_call.{tool_id}", json.dumps(tool_result))
                                    current_tool_call = None

                        yield response

                except Exception as err:
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    raise
                finally:
                    span.set_status(Status(StatusCode.OK))
                    if len(seen_tool_calls) > 0:
                        span.set_attribute("phidata.agent.total_tool_calls", len(seen_tool_calls))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method

class PhiDataSpanAttributes:
    span: Span
    agent_data: dict

    def __init__(self, span: Span, instance) -> None:
        self.span = span
        self.instance = instance
        self.agent_data = {
            "memory": {},
            "model": {},
            "tools": [],
        }

        self.run()

    def run(self):
        instance_attrs = {
            "agent_id": self.instance.agent_id,
            "session_id": self.instance.session_id,
            "name": self.instance.name,
            "markdown": self.instance.markdown,
            "reasoning": self.instance.reasoning,
            "add_references": self.instance.add_references,
            "show_tool_calls": self.instance.show_tool_calls,
            "stream": self.instance.stream,
            "stream_intermediate_steps": self.instance.stream_intermediate_steps,
        }
        
        for key, value in instance_attrs.items():
            if value is not None:
                set_span_attribute(self.span, f"phidata.agent.{key}", str(value))

        if self.instance.model:
            model_attrs = {
                "id": self.instance.model.id,
                "name": self.instance.model.name,
                "provider": self.instance.model.provider,
                "structured_outputs": self.instance.model.structured_outputs,
                "supports_structured_outputs": self.instance.model.supports_structured_outputs,
            }
            for key, value in model_attrs.items():
                if value is not None:
                    set_span_attribute(self.span, f"phidata.agent.model.{key}", str(value))

            if hasattr(self.instance.model, 'metrics') and self.instance.model.metrics:
                metrics = _extract_metrics(self.instance.model.metrics)
                set_span_attribute(self.span, "phidata.agent.model.metrics", json.dumps(metrics))

        if self.instance.tools:
            tool_list = []
            for tool in self.instance.tools:
                if hasattr(tool, "name"):
                    tool_list.append(tool.name)
                elif hasattr(tool, "__name__"):
                    tool_list.append(tool.__name__)
            set_span_attribute(self.span, "phidata.agent.tools", str(tool_list))

        if self.instance.memory:
            memory_attrs = {
                "create_session_summary": self.instance.memory.create_session_summary,
                "create_user_memories": self.instance.memory.create_user_memories,
                "update_session_summary_after_run": self.instance.memory.update_session_summary_after_run,
                "update_user_memories_after_run": self.instance.memory.update_user_memories_after_run,
            }
            for key, value in memory_attrs.items():
                if value is not None:
                    set_span_attribute(self.span, f"phidata.agent.memory.{key}", str(value))
