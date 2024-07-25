from langtrace_python_sdk.constants.instrumentation.ollama import APIS
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    set_event_completion,
    set_event_completion_chunk,
)
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace.trace_attributes import LLMSpanAttributes, Event
from opentelemetry.trace import SpanKind
import json
from opentelemetry.trace.status import Status, StatusCode
from langtrace.trace_attributes import SpanAttributes


def generic_patch(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[operation_name]
        service_provider = SERVICE_PROVIDERS["OLLAMA"]
        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(
                kwargs,
                prompts=kwargs.get("messages", None),
            ),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: api["ENDPOINT"],
            SpanAttributes.LLM_RESPONSE_FORMAT: kwargs.get("format"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(
            f'ollama.{api["METHOD"]}', kind=SpanKind.CLIENT
        ) as span:
            _set_input_attributes(span, kwargs, attributes)

            try:
                result = wrapped(*args, **kwargs)
                if result:
                    if span.is_recording():

                        if kwargs.get("stream"):
                            return _handle_streaming_response(
                                span, result, api["METHOD"]
                            )

                        _set_response_attributes(span, result)
                        span.set_status(Status(StatusCode.OK))

                span.end()
                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def ageneric_patch(operation_name, version, tracer):
    async def traced_method(wrapped, instance, args, kwargs):
        api = APIS[operation_name]
        service_provider = SERVICE_PROVIDERS["OLLAMA"]
        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: api["ENDPOINT"],
            SpanAttributes.LLM_RESPONSE_FORMAT: kwargs.get("format"),
            **get_extra_attributes(),
        }
        attributes = LLMSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(api["METHOD"], kind=SpanKind.CLIENT) as span:
            _set_input_attributes(span, kwargs, attributes)
            try:
                result = await wrapped(*args, **kwargs)
                if result:
                    if span.is_recording():
                        if kwargs.get("stream"):
                            return _ahandle_streaming_response(
                                span, result, api["METHOD"]
                            )

                        _set_response_attributes(span, result)
                        span.set_status(Status(StatusCode.OK))
                span.end()
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


@silently_fail
def _set_response_attributes(span, response):

    input_tokens = response.get("prompt_eval_count") or 0
    output_tokens = response.get("eval_count") or 0
    total_tokens = input_tokens + output_tokens

    if total_tokens > 0:
        set_span_attribute(span, SpanAttributes.LLM_USAGE_PROMPT_TOKENS, input_tokens)
        set_span_attribute(
            span, SpanAttributes.LLM_USAGE_COMPLETION_TOKENS, output_tokens
        )
        set_span_attribute(span, SpanAttributes.LLM_USAGE_TOTAL_TOKENS, total_tokens)

    set_span_attribute(
        span,
        SpanAttributes.LLM_RESPONSE_FINISH_REASON,
        response.get("done_reason"),
    )
    if "message" in response:
        set_event_completion(span, [response.get("message")])

    if "response" in response:
        set_event_completion(
            span, [{"role": "assistant", "content": response.get("response")}]
        )


@silently_fail
def _set_input_attributes(span, kwargs, attributes):
    options = kwargs.get("options")

    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)

    if "options" in kwargs:
        set_span_attribute(
            span,
            SpanAttributes.LLM_REQUEST_TEMPERATURE,
            options.get("temperature"),
        )
        set_span_attribute(span, SpanAttributes.LLM_REQUEST_TOP_P, options.get("top_p"))
        set_span_attribute(
            span,
            SpanAttributes.LLM_FREQUENCY_PENALTY,
            options.get("frequency_penalty"),
        )
        set_span_attribute(
            span,
            SpanAttributes.LLM_PRESENCE_PENALTY,
            options.get("presence_penalty"),
        )


def _handle_streaming_response(span, response, api):
    accumulated_tokens = None
    if api == "chat":
        accumulated_tokens = {"message": {"content": "", "role": ""}}
    if api == "completion":
        accumulated_tokens = {"response": ""}
    span.add_event(Event.STREAM_START.value)
    try:
        for chunk in response:
            if api == "chat":
                accumulated_tokens["message"]["content"] += chunk["message"]["content"]
                accumulated_tokens["message"]["role"] = chunk["message"]["role"]
            if api == "generate":
                accumulated_tokens["response"] += chunk["response"]

            set_event_completion_chunk(
                span, chunk.get("response") or chunk.get("message").get("content")
            )

        _set_response_attributes(span, chunk | accumulated_tokens)
    finally:
        # Finalize span after processing all chunks
        span.add_event(Event.STREAM_END.value)
        span.set_status(StatusCode.OK)
        span.end()

    return response


async def _ahandle_streaming_response(span, response, api):
    accumulated_tokens = None
    if api == "chat":
        accumulated_tokens = {"message": {"content": "", "role": ""}}
    if api == "completion":
        accumulated_tokens = {"response": ""}

    span.add_event(Event.STREAM_START.value)
    try:
        async for chunk in response:
            if api == "chat":
                accumulated_tokens["message"]["content"] += chunk["message"]["content"]
                accumulated_tokens["message"]["role"] = chunk["message"]["role"]
            if api == "generate":
                accumulated_tokens["response"] += chunk["response"]

            set_event_completion_chunk(span, chunk)
        _set_response_attributes(span, chunk | accumulated_tokens)
    finally:
        # Finalize span after processing all chunks
        span.add_event(Event.STREAM_END.value)
        span.set_status(StatusCode.OK)
        span.end()

    return response
