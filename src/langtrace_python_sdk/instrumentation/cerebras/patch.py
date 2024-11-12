from langtrace_python_sdk.instrumentation.groq.patch import extract_content
from opentelemetry.trace import SpanKind
from langtrace_python_sdk.utils.llm import (
    get_llm_request_attributes,
    get_langtrace_attributes,
    get_extra_attributes,
    get_llm_url,
    is_streaming,
    set_event_completion,
    set_span_attributes,
    StreamWrapper,
)
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace.trace_attributes import SpanAttributes
from langtrace_python_sdk.utils import handle_span_error, set_span_attribute


def chat_completions_create(version: str, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        llm_prompts = []
        for message in kwargs.get("messages", []):
            llm_prompts.append(message)

        span_attributes = {
            **get_langtrace_attributes(version, SERVICE_PROVIDERS["CEREBRAS"]),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            **get_extra_attributes(),
        }

        span_name = f"{span_attributes[SpanAttributes.LLM_OPERATION_NAME]} {span_attributes[SpanAttributes.LLM_REQUEST_MODEL]}"
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:

            try:
                _set_input_attributes(span, kwargs, span_attributes)
                result = wrapped(*args, **kwargs)
                if is_streaming(kwargs):
                    return StreamWrapper(result, span)

                if span.is_recording():
                    _set_response_attributes(span, result)
                span.end()
                return result

            except Exception as error:
                handle_span_error(span, error)
                raise

    return traced_method


def async_chat_completions_create(version: str, tracer):
    async def traced_method(wrapped, instance, args, kwargs):
        llm_prompts = []
        for message in kwargs.get("messages", []):
            llm_prompts.append(message)

        span_attributes = {
            **get_langtrace_attributes(version, SERVICE_PROVIDERS["CEREBRAS"]),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            **get_extra_attributes(),
        }

        span_name = f"{span_attributes[SpanAttributes.LLM_OPERATION_NAME]} {span_attributes[SpanAttributes.LLM_REQUEST_MODEL]}"
        with tracer.start_as_current_span(
            name=span_name,
            kind=SpanKind.CLIENT,
            attributes=span_attributes,
            end_on_exit=False,
        ) as span:

            try:
                _set_input_attributes(span, kwargs, span_attributes)
                result = await wrapped(*args, **kwargs)
                if is_streaming(kwargs):
                    return StreamWrapper(result, span)

                if span.is_recording():
                    _set_response_attributes(span, result)
                span.end()
                return result

            except Exception as error:
                handle_span_error(span, error)
                raise

    return traced_method


@silently_fail
def _set_response_attributes(span, result):
    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, result.model)

    if getattr(result, "id", None):
        set_span_attribute(span, SpanAttributes.LLM_RESPONSE_ID, result.id)

    if getattr(result, "choices", None):
        responses = [
            {
                "role": (
                    choice.message.role
                    if choice.message and choice.message.role
                    else "assistant"
                ),
                "content": extract_content(choice),
                **(
                    {"content_filter_results": choice.content_filter_results}
                    if hasattr(choice, "content_filter_results")
                    else {}
                ),
            }
            for choice in result.choices
        ]
        set_event_completion(span, responses)
    # Get the usage
    if getattr(result, "usage", None):
        set_span_attribute(
            span,
            SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
            result.usage.prompt_tokens,
        )
        set_span_attribute(
            span,
            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
            result.usage.completion_tokens,
        )


@silently_fail
def _set_input_attributes(span, kwargs, attributes):
    set_span_attributes(span, attributes)
