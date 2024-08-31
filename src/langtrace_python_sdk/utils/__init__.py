from langtrace_python_sdk.types import NOT_GIVEN
from .sdk_version_checker import SDKVersionChecker
from opentelemetry.trace import Span
from langtrace.trace_attributes import SpanAttributes
import os


def set_span_attribute(span: Span, name, value):
    if value is not None:
        if value != "" or value != NOT_GIVEN:
            if name == SpanAttributes.LLM_PROMPTS:
                set_event_prompt(span, value)
            else:
                span.set_attribute(name, value)
    return


def set_event_prompt(span: Span, prompt):
    enabled = os.environ.get("TRACE_PROMPT_COMPLETION_DATA", "true")
    if enabled.lower() == "false":
        return

    span.add_event(
        name=SpanAttributes.LLM_CONTENT_PROMPT,
        attributes={
            SpanAttributes.LLM_PROMPTS: prompt,
        },
    )


def check_if_sdk_is_outdated():
    SDKVersionChecker().check()
    return
