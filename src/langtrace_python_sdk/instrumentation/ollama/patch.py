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
from langtrace.trace_attributes import Event, LLMSpanAttributes


def generic_patch(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[operation_name]
        print("KWARGSSS", kwargs)
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
            "url.full": "",
            "llm.api": "",
            "llm.prompts": json.dumps(
                [{"role": "user", "content": kwargs.get("prompt", [])}]
            ),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(
            f'ollama.{api["METHOD"]}', kind=SpanKind.CLIENT
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                result = wrapped(*args, **kwargs)
                if result:
                    if span.is_recording():

                        if kwargs.get("stream"):
                            _handle_streaming_response(span, result)

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
                result = await wrapped(*args, **kwargs)
                if result:
                    if span.is_recording():
                        if kwargs.get("stream"):
                            return _accumulate_streaming_response(span, result)

                        _set_response_attributes(span, result)
                        span.set_status(Status(StatusCode.OK))
                    _set_response_attributes(span, result)
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


def _set_response_attributes(span, response):
    input_tokens = response.get("prompt_eval_count") or 0
    output_tokens = response.get("eval_count") or 0
    total_tokens = input_tokens + output_tokens
    usage_dict = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
    set_span_attribute(span, "llm.token.counts", json.dumps(usage_dict))
    set_span_attribute(span, "llm.finish_reason", response.get("done_reason"))


def _handle_streaming_response(span, response):
    span.add_event(Event.STREAM_START.value)
    for chunk in response:
        print("CHUNK", chunk)
    return response
