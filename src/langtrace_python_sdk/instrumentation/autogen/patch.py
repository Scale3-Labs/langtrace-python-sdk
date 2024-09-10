from langtrace_python_sdk.utils.llm import (
    get_langtrace_attributes,
    get_extra_attributes,
    get_span_name,
    set_span_attributes,
    get_llm_request_attributes,
    set_event_completion,
)
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace.trace_attributes import FrameworkSpanAttributes

from opentelemetry.trace import Tracer, SpanKind
import pprint


def patch_autogen(name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        print("kwargs", kwargs)
        # print("instance", pprint.pprint(instance.__dict__))

        service_provider = SERVICE_PROVIDERS["AUTOGEN"]

        span_attributes = {
            **get_langtrace_attributes(
                version=version,
                service_provider=service_provider,
                vendor_type="framework",
            ),
            **get_llm_request_attributes(kwargs, prompts=kwargs.get("messages")),
            **get_extra_attributes(),
        }
        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(
            name=get_span_name(name), kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                result = wrapped(*args, **kwargs)
                set_response_attributes(span, result)

                return result

            except Exception as e:
                print("error", e)

    return traced_method


def set_response_attributes(span, result):
    chat_history = getattr(result, "chat_history", None)
    summary = getattr(result, "summary", None)
    usage = getattr(result, "cost", None)
    print(result)
    if chat_history:
        set_event_completion(span, chat_history)

    if usage:
        print("usage", usage)
