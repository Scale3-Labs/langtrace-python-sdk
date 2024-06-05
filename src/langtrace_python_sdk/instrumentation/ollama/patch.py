from langtrace_python_sdk.constants.instrumentation.ollama import APIS
from importlib_metadata import version as v
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from opentelemetry import baggage
from langtrace.trace_attributes import LLMSpanAttributes
from opentelemetry.trace import SpanKind
import json
from opentelemetry.trace.status import Status, StatusCode


def generic_patch(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[operation_name]
        service_provider = SERVICE_PROVIDERS["OLLAMA"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "llm.model": kwargs.get("model"),
            "llm.stream": kwargs.get("stream"),
            "llm.prompts": json.dumps(
                [{"role": "user", "content": kwargs.get("prompt", [])}]
            ),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(api["METHOD"], kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                result = wrapped(*args, **kwargs)
                return result
            except Exception as err:
                print("ERRORR", err)
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method
