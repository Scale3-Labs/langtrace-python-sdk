"""
This module contains the patching logic for the OpenAI library."""
import json

from langtrace.trace_attributes import Event, LLMSpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from langtrace_python_sdk.utils.llm import (calculate_prompt_tokens,
                                            estimate_tokens)


def images_generate(original_method, version, tracer):
    """
    Wrap the `generate` method of the `Images` class to trace it.
    """
    def traced_method(wrapped, instance, args, kwargs):
        base_url = str(instance._client._base_url) if hasattr(
            instance, '_client') and hasattr(instance._client, '_base_url') else ""
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["IMAGES_GENERATION"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.stream": kwargs.get('stream'),
            "llm.prompts": json.dumps([kwargs.get('prompt', [])])
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(APIS["IMAGES_GENERATION"]["METHOD"],
                                          kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = original_method(*args, **kwargs)
                if kwargs.get('stream') is False or kwargs.get('stream') is None:
                    data = result.data[0] if hasattr(
                        result, 'data') and len(result.data) > 0 else {}
                    response = [{
                        "url": data.url if hasattr(data, 'url') else "",
                        "revised_prompt": data.revised_prompt if
                        hasattr(data, 'revised_prompt') else "",
                    }]
                    span.set_attribute(
                        "llm.responses", json.dumps(response))

                span.set_status(StatusCode.OK)
                return result
            except Exception as e:
                # Record the exception in the span
                span.record_exception(e)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""
    def traced_method(wrapped, instance, args, kwargs):
        base_url = str(instance._client._base_url) if hasattr(
            instance, '_client') and hasattr(instance._client, '_base_url') else ""
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.prompts": json.dumps(kwargs.get('messages', [])),
            "llm.stream": kwargs.get('stream'),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get('temperature') is not None:
            attributes.llm_temperature = kwargs.get('temperature')
        if kwargs.get('top_p') is not None:
            attributes.llm_top_p = kwargs.get('top_p')
        if kwargs.get('user') is not None:
            attributes.llm_user = kwargs.get('user')
        if kwargs.get('functions') is not None:
            attributes.llm_function_prompts = json.dumps(
                kwargs.get('functions'))

        # TODO(Karthik): Gotta figure out how to handle streaming with context
        # with tracer.start_as_current_span(APIS["CHAT_COMPLETION"]["METHOD"],
        #                                   kind=SpanKind.CLIENT) as span:
        span = tracer.start_span(
            APIS["CHAT_COMPLETION"]["METHOD"], kind=SpanKind.CLIENT)
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = original_method(*args, **kwargs)
            if kwargs.get('stream') is False:
                if hasattr(result, 'choices') and result.choices is not None:
                    responses = [
                        {
                            "message": choice.message.content if choice.message and
                            choice.message.content else choice.message.function_call.arguments
                            if choice.message and
                            choice.message.function_call.arguments else "",
                            **({"content_filter_results": choice["content_filter_results"]}
                               if "content_filter_results" in choice else {})
                        }
                        for choice in result.choices
                    ]
                    span.set_attribute(
                        "llm.responses", json.dumps(responses))
                else:
                    responses = []
                    span.set_attribute(
                        "llm.responses", json.dumps(responses))
                if hasattr(result, 'system_fingerprint') and \
                        result.system_fingerprint is not None:
                    span.set_attribute(
                        "llm.system.fingerprint", result.system_fingerprint)
                # Get the usage
                if hasattr(result, 'usage') and result.usage is not None:
                    usage = result.usage
                    if usage is not None:
                        usage_dict = {
                            "prompt_tokens": result.usage.prompt_tokens,
                            "completion_tokens": usage.completion_tokens,
                            "total_tokens": usage.total_tokens
                        }
                        span.set_attribute(
                            "llm.token.counts", json.dumps(usage_dict))
                span.set_status(StatusCode.OK)
                span.end()
                return result
            else:
                prompt_tokens = calculate_prompt_tokens(json.dumps(
                    kwargs.get('messages', {})[0]), kwargs.get('model'))
                return handle_streaming_response(result, span, prompt_tokens,
                                                 function_call=kwargs.get(
                                                     'functions')
                                                 is not None)
        except Exception as e:
            # Record the exception in the span
            span.record_exception(e)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    def handle_streaming_response(result, span, prompt_tokens, function_call=False):
        """Process and yield streaming response chunks."""
        result_content = []
        span.add_event(Event.STREAM_START.value)
        completion_tokens = 0
        try:
            for chunk in result:
                if hasattr(chunk, 'choices') and chunk.choices is not None:
                    token_counts = [
                        estimate_tokens(choice.delta.content) if choice.delta
                        and choice.delta.content
                        else estimate_tokens(choice.delta.function_call.arguments)
                        if choice.delta.function_call and
                        choice.delta.function_call.arguments else 0
                        for choice in chunk.choices
                    ]
                    completion_tokens += sum(token_counts)
                    content = [
                        choice.delta.content if choice.delta and choice.delta.content
                        else choice.delta.function_call.arguments if choice.delta.function_call and
                        choice.delta.function_call.arguments else ""
                        for choice in chunk.choices
                    ]
                else:
                    content = []
                span.add_event(Event.STREAM_OUTPUT.value, {
                    "response": "".join(content)
                })
                result_content.append(
                    content[0] if len(content) > 0 else "")
                yield chunk
        finally:

            # Finalize span after processing all chunks
            span.add_event(Event.STREAM_END.value)
            span.set_attribute("llm.token.counts", json.dumps({
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }))
            if function_call is False:
                span.set_attribute("llm.responses", json.dumps(
                    {"message": {"role": "assistant", "content": "".join(result_content)}}))
            else:
                span.set_attribute("llm.responses", json.dumps(
                    {"message": {"role": "assistant", "function_call": "".join(result_content)}}))
            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
    return traced_method


def embeddings_create(original_method, version, tracer):
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """
    def traced_method(wrapped, instance, args, kwargs):
        base_url = str(instance._client._base_url) if hasattr(
            instance, '_client') and hasattr(instance._client, '_base_url') else ""

        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.prompts": "",
        }

        attributes = LLMSpanAttributes(**span_attributes)
        kwargs.get('encoding_format')

        if kwargs.get('encoding_format') is not None:
            attributes.llm_encoding_format = kwargs.get('encoding_format')
        if kwargs.get('dimensions') is not None:
            attributes["llm.dimensions"] = kwargs.get('dimensions')
        if kwargs.get('user') is not None:
            attributes["llm.user"] = kwargs.get('user')

        with tracer.start_as_current_span(APIS["EMBEDDINGS_CREATE"]["METHOD"],
                                          kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = original_method(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as e:
                # Record the exception in the span
                span.record_exception(e)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method
