from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.instrumentation.openai.patch import StreamWrapper
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import (
    calculate_prompt_tokens,
    get_extra_attributes,
    get_llm_request_attributes,
    get_langtrace_attributes,
    get_streaming_tokens,
    is_streaming,
    set_usage_attributes,
)
from langtrace.trace_attributes import LLMSpanAttributes, SpanAttributes, Event
from langtrace_python_sdk.utils.silently_fail import silently_fail
from openai import NOT_GIVEN
from opentelemetry.trace import SpanKind, StatusCode, Status
from opentelemetry import trace
from opentelemetry.trace.propagation import set_span_in_context

import json


def litellm_patch(name, tracer, version):
    def traced_method(wrapped, instance, args, kwargs):

        print("Name", name)
        service_provider = SERVICE_PROVIDERS["LITELLM"]
        prompts = kwargs.get("messages")
        optional_params = kwargs.get("optional_params", {})
        options = {**kwargs, **optional_params}

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(options, prompts=prompts),
            SpanAttributes.LLM_URL: kwargs.get("api_base"),
            SpanAttributes.LLM_PATH: "completion",
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)
        with tracer.start_span(
            name=name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            try:
                set_input_attributes(span, attributes)
                result = wrapped(*args, **kwargs)
                if is_streaming(kwargs):
                    return StreamWrapper(
                        stream=result,
                        span=trace.get_current_span(),
                        prompt_tokens=get_streaming_tokens(kwargs),
                        function_call=kwargs.get("functions") is not None,
                        tool_calls=kwargs.get("tools") is not None,
                    )

                else:
                    print("not streaming", span)
                    set_response_attributes(span, result)
                    return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                span.end()
                raise

    return traced_method


def async_litellm_patch(name, tracer, version):
    async def traced_method(wrapped, instance, args, kwargs):
        print("Name", name)
        service_provider = SERVICE_PROVIDERS["LITELLM"]
        prompts = kwargs.get("messages")
        optional_params = kwargs.get("optional_params", {})
        options = {**kwargs, **optional_params}

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(options, prompts=prompts),
            SpanAttributes.LLM_URL: kwargs.get("api_base"),
            SpanAttributes.LLM_PATH: "completion",
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)
        span = tracer.start_span(
            name=name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        with tracer.start_span(
            name=name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            try:
                set_input_attributes(span, attributes)
                result = await wrapped(*args, **kwargs)
                if is_streaming(kwargs):
                    return StreamWrapper(
                        stream=result,
                        span=span,
                        prompt_tokens=get_streaming_tokens(kwargs),
                        function_call=kwargs.get("functions") is not None,
                        tool_calls=kwargs.get("tools") is not None,
                    )

                else:
                    set_response_attributes(span, result)
                    return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                span.end()
                raise

    return traced_method


@silently_fail
def set_input_attributes(span, attributes):
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)


@silently_fail
def set_response_attributes(span, result):
    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, result.model)
    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_ID, result.id)
    set_span_attribute(
        span, SpanAttributes.LLM_SYSTEM_FINGERPRINT, result.system_fingerprint
    )
    set_usage_attributes(span, result.usage)

    for choice in result.choices:
        print("Choice", span.is_recording())
        set_span_attribute(
            span, SpanAttributes.LLM_RESPONSE_FINISH_REASON, choice.finish_reason
        )
        set_span_attribute(
            span, SpanAttributes.LLM_COMPLETIONS, json.dumps(choice.message)
        )
