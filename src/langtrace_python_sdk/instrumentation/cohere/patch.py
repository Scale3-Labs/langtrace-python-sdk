"""
This module contains the patching logic for the Anthropic library."""

import json

from langtrace.trace_attributes import Event, LLMSpanAttributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from langtrace_python_sdk.constants.instrumentation.common import (LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, SERVICE_PROVIDERS)

def embed_create(original_method, version, tracer):
    """Wrap the `embed_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["COHERE"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
         
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["EMBED_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": "",
            **(extra_attributes if extra_attributes is not None else {})
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("top_p") is not None:
            attributes.llm_top_p = kwargs.get("top_p")
        if kwargs.get("top_k") is not None:
            attributes.llm_top_p = kwargs.get("top_k")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")

        span = tracer.start_span(
            APIS["EMBED_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            span.set_status(StatusCode.OK)
            span.end()
            return result
            
        except Exception as e:
            # Record the exception in the span
            span.record_exception(e)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise
    return traced_method

def chat_create(original_method, version, tracer):
    """Wrap the `chat_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["COHERE"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        # extract system from kwargs and attach as a role to the prompts
        # we do this to keep it consistent with the openai
        prompts = json.dumps(kwargs.get("message", " "))

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["CHAT_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": prompts,
            "llm.stream": False,
            **(extra_attributes if extra_attributes is not None else {})
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("top_p") is not None:
            attributes.llm_top_p = kwargs.get("top_p")
        if kwargs.get("top_k") is not None:
            attributes.llm_top_p = kwargs.get("top_k")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")

        span = tracer.start_span(
            APIS["CHAT_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if hasattr(result, "chat_history") and result.text is not None:
                responses = [
                    {
                        "message": {
                            "role": (
                                choice.role
                            ),
                            "content": (
                                choice.message
                            )
                        }
                    }
                    for choice in result.chat_history
                ]
                span.set_attribute("llm.responses", json.dumps(responses))
            else:
                responses = []
                span.set_attribute("llm.responses", json.dumps(responses))
            if (
                hasattr(result, "system_fingerprint")
                and result.system_fingerprint is not None
            ):
                span.set_attribute(
                    "llm.system.fingerprint", result.system_fingerprint
                )
            # Get the usage
            if hasattr(result, "meta") and result.meta is not None:
                usage = result.meta['tokens']
                if usage is not None:
                    usage_dict = {
                        "input_tokens": usage['input_tokens'],
                        "output_tokens": usage['output_tokens'],
                        "total_tokens":  usage['input_tokens'] + usage['output_tokens'],
                    }
                    span.set_attribute("llm.token.counts", json.dumps(usage_dict))
            span.set_status(StatusCode.OK)
            span.end()
            return result

        except Exception as e:
            # Record the exception in the span
            span.record_exception(e)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise
    return traced_method

def chat_stream(original_method, version, tracer):
    """Wrap the `messages_stream` method."""

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["COHERE"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        prompts = json.dumps(kwargs.get("message", ""))

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["CHAT_STREAM"]["ENDPOINT"],
            "llm.model": "",
            "llm.prompts": prompts,
            "llm.stream": True,
            **(extra_attributes if extra_attributes is not None else {})
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("top_p") is not None:
            attributes.llm_top_p = kwargs.get("top_p")
        if kwargs.get("top_k") is not None:
            attributes.llm_top_p = kwargs.get("top_k")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")

        span = tracer.start_span(
            APIS["CHAT_STREAM"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)

            span.add_event(Event.STREAM_START.value)
            for chunk in result:
                if(hasattr(chunk, "event_type") and chunk.event_type is not None and chunk.event_type == "stream-end"):
                    if hasattr(chunk, "response") and chunk.response is not None:
                        span.set_attribute("llm.responses", json.dumps(chunk.response.text))
                        if(hasattr(chunk.response, "meta") and chunk.response.meta is not None):
                            usage = chunk.response.meta['tokens']
                            if usage is not None:
                                usage_dict = {
                                    "input_tokens": usage['input_tokens'],
                                    "output_tokens": usage['output_tokens'],
                                    "total_tokens":  usage['input_tokens'] + usage['output_tokens'],
                                }
                                span.set_attribute("llm.token.counts", json.dumps(usage_dict))

            span.add_event(Event.STREAM_END.value)
            span.set_status(StatusCode.OK)
            span.end()
            return result
        
            # return handle_streaming_response(result, span)
        except Exception as e:
            # Record the exception in the span
            span.record_exception(e)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    # return the wrapped method
    return traced_method
