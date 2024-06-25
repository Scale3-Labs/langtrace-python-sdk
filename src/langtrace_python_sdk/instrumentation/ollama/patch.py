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
from langtrace.trace_attributes import LLMSpanAttributes, Event
from opentelemetry.trace import SpanKind
import json
from opentelemetry.trace.status import Status, StatusCode


def generic_patch(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
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
            "url.full": base_url,
            "llm.api": api["ENDPOINT"],
            "llm.response_format": kwargs.get("format"),
            **(extra_attributes if extra_attributes is not None else {}),
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
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "url.full": "",
            "llm.api": "",
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "llm.model": kwargs.get("model"),
            "llm.stream": kwargs.get("stream"),
            "llm.response_format": kwargs.get("format"),
            "http.timeout": (
                kwargs.get("keep_alive") if "keep_alive" in kwargs else None
            ),
            **(extra_attributes if extra_attributes is not None else {}),
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
    usage_dict = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }

    if total_tokens > 0:
        set_span_attribute(span, "llm.token.counts", json.dumps(usage_dict))
    set_span_attribute(span, "llm.finish_reason", response.get("done_reason"))
    if "message" in response:
        set_span_attribute(span, "llm.responses", json.dumps([response.get("message")]))

    if "response" in response:
        set_span_attribute(
            span,
            "llm.responses",
            json.dumps([{"role": "assistant", "content": response.get("response")}]),
        )


@silently_fail
def _set_input_attributes(span, kwargs, attributes):
    options = kwargs.get("options")

    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)
    if "messages" in kwargs:
        set_span_attribute(
            span,
            "llm.prompts",
            json.dumps(kwargs.get("messages", [])),
        )
    if "prompt" in kwargs:
        set_span_attribute(
            span,
            "llm.prompts",
            json.dumps([{"role": "user", "content": kwargs.get("prompt", "")}]),
        )
    if "options" in kwargs:
        set_span_attribute(span, "llm.temperature", options.get("temperature"))
        set_span_attribute(span, "llm.top_p", options.get("top_p"))
        set_span_attribute(
            span, "llm.frequency_penalty", options.get("frequency_penalty")
        )
        set_span_attribute(
            span, "llm.presence_penalty", options.get("presence_penalty")
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

        _set_response_attributes(span, chunk | accumulated_tokens)
    finally:
        # Finalize span after processing all chunks
        span.add_event(Event.STREAM_END.value)
        span.set_status(StatusCode.OK)
        span.end()

    return response
