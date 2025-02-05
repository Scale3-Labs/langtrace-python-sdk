import json
from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import Span, SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.utils.llm import set_span_attributes
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs


def patch_graphlit_operation(operation_name, version, tracer: Tracer):
    async def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["GRAPHLIT"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        span_attributes["langchain.metadata"] = serialize_kwargs(**kwargs)
        span_attributes["langchain.inputs"] = serialize_args(*args)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=f"graphlit.{operation_name}", kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                result = await wrapped(*args, **kwargs)
                
                if result:
                    operation_result = json.loads(result.model_dump_json())[operation_name]
                    if operation_name == "complete_conversation" or operation_name == "prompt_conversation" or operation_name == "format_conversation":
                        set_graphlit_conversation_attributes(span, operation_result)
                    else:
                        for key, value in operation_result.items():
                            span.set_attribute(f"graphlit.{operation_name}.{key}", str(value))

                    span.set_status(Status(StatusCode.OK))

                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def set_graphlit_conversation_attributes(span: Span, response):
    if not response or "message" not in response:
        return

    span.set_attribute(f"graphlit.conversation.id", response['conversation']['id'])

    for key, value in response['message'].items():
        span.set_attribute(f"graphlit.conversation.{key}", str(value))
