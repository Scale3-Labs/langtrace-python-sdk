from openai import NOT_GIVEN
from .sdk_version_checker import SDKVersionChecker
from opentelemetry.trace import Span
from langtrace.trace_attributes import SpanAttributes


def set_span_attribute(span: Span, name, value):
    if value is not None:
        if value != "" or value != NOT_GIVEN:
            if name == SpanAttributes.LLM_PROMPTS:
                span.add_event(
                    name=SpanAttributes.LLM_CONTENT_PROMPT,
                    attributes={
                        SpanAttributes.LLM_PROMPTS: value,
                    },
                )
            else:
                span.set_attribute(name, value)
    return


def check_if_sdk_is_outdated():
    SDKVersionChecker().check()
    return
