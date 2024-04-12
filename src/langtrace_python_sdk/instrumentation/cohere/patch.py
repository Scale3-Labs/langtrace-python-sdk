"""
This module contains the patching logic for the Anthropic library."""

import json

from langtrace.trace_attributes import Event, LLMSpanAttributes
from opentelemetry import baggage
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
        if kwargs.get("p") is not None:
            attributes.llm_top_p = kwargs.get("p")
        if kwargs.get("k") is not None:
            attributes.llm_top_p = kwargs.get("k")
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

        except Exception as error:
            # Record the exception in the span
            span.record_exception(error)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(error)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise
    return traced_method


def chat_create(original_method, version, tracer):
    """Wrap the `chat_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        message = kwargs.get("message", "")
        prompts = json.dumps([
            {
                "role": "USER",
                "content": message
            }
        ])
        preamble = kwargs.get("preamble")
        if preamble:
            prompts = json.dumps(
                [{"role": "system", "content": preamble}] + [{"role": "USER", "content": message}]
            )

        chat_history = kwargs.get("chat_history")
        if chat_history:
            history = [
                {
                    "message": {
                        "role": (
                            item.get("role") if item.get("role") is not None else "USER"
                        ),
                        "content": (
                            item.get("message") if item.get("message") is not None else ""
                        )
                    }
                }
                for item in chat_history
            ]
            prompts = prompts + json.dumps(history)

        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": APIS["CHAT_CREATE"]["URL"],
            "llm.api": APIS["CHAT_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model") if kwargs.get("model") is not None else "command-r",
            "llm.stream": False,
            "llm.prompts": prompts,
            **(extra_attributes if extra_attributes is not None else {})
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("max_tokens") is not None:
            attributes.max_tokens = kwargs.get("max_tokens")
        if kwargs.get("max_input_tokens") is not None:
            attributes.max_input_tokens = kwargs.get("max_input_tokens")
        if kwargs.get("p") is not None:
            attributes.llm_top_p = kwargs.get("p")
        if kwargs.get("k") is not None:
            attributes.llm_top_p = kwargs.get("k")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")
        if kwargs.get("conversation_id") is not None:
            attributes.conversation_id = kwargs.get("conversation_id")
        if kwargs.get("seed") is not None:
            attributes.seed = kwargs.get("seed")
        if kwargs.get("frequency_penalty") is not None:
            attributes.frequency_penalty = kwargs.get("frequency_penalty")
        if kwargs.get("presence_penalty") is not None:
            attributes.presence_penalty = kwargs.get("presence_penalty")
        if kwargs.get("connectors") is not None:
            # stringify the list of objects
            attributes.llm_connectors = json.dumps(kwargs.get("connectors"))
        if kwargs.get("tools") is not None:
            # stringify the list of objects
            attributes.llm_tools = json.dumps(kwargs.get("tools"))
        if kwargs.get("tool_results") is not None:
            # stringify the list of objects
            attributes.llm_tool_results = json.dumps(kwargs.get("tool_results"))

        span = tracer.start_span(
            APIS["CHAT_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        )

        # Set the attributes on the span
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)

            # Set the response attributes
            if (hasattr(result, "generation_id")) and (result.generation_id is not None):
                span.set_attribute("llm.generation_id", result.generation_id)
            if (hasattr(result, "response_id")) and (result.response_id is not None):
                span.set_attribute("llm.response_id", result.response_id)
            if (hasattr(result, "is_search_required")) and (result.is_search_required is not None):
                span.set_attribute("llm.is_search_required", result.is_search_required)

            if kwargs.get("stream") is False or kwargs.get("stream") is None:
                if hasattr(result, "text") and result.text is not None:
                    if hasattr(result, "chat_history") and result.chat_history is not None:
                        responses = [
                            {
                                "message": {
                                    "role": (
                                        item.role if hasattr(item, "role") and item.role is not None else "USER"
                                    ),
                                    "content": (
                                        item.message if hasattr(item, "message") and item.message is not None else ""
                                    )
                                }
                            }
                            for item in result.chat_history
                        ]
                        span.set_attribute("llm.responses", json.dumps(responses))
                    else:
                        responses = [{
                            "message": {
                                "role": "CHATBOT",
                                "content": result.text
                            }
                        }]
                        span.set_attribute("llm.responses", json.dumps(responses))
                else:
                    responses = []
                    span.set_attribute("llm.responses", json.dumps(responses))

                # Get the usage
                if hasattr(result, "meta") and result.meta is not None:
                    if hasattr(result.meta, "billed_units") and result.meta.billed_units is not None:
                        usage = result.meta.billed_units
                        if usage is not None:
                            usage_dict = {
                                "input_tokens": usage.input_tokens if usage.input_tokens is not None else 0,
                                "output_tokens": usage.output_tokens if usage.output_tokens is not None else 0,
                                "total_tokens": usage.input_tokens + usage.output_tokens if usage.input_tokens is not None and usage.output_tokens is not None else 0,
                            }
                            span.set_attribute("llm.token.counts", json.dumps(usage_dict))
                span.set_status(StatusCode.OK)
                span.end()
                return result
            else:
                # For older version, stream was passed as a parameter
                return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
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
