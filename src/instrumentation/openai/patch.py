import json

from langtrace.trace_attributes import Event, OpenAISpanAttributes
from opentelemetry import trace
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.status import Status, StatusCode

from constants import SERVICE_PROVIDERS
from instrumentation.openai.lib.apis import APIS


def images_generate(original_method, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "service.provider": service_provider,
            "url.full": APIS["IMAGES_GENERATION"]["ENDPOINT"],
            "llm.api": APIS["IMAGES_GENERATION"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.stream": kwargs.get('stream'),
            "llm.prompts": json.dumps(kwargs.get('prompts', [])),
        }

        attributes = OpenAISpanAttributes(**span_attributes)

        with tracer.start_as_current_span(APIS["IMAGES_GENERATION"]["METHOD"], kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                  span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = original_method(*args, **kwargs)
                if kwargs.get('stream') is False:
                    span.set_attribute("llm.responses", json.dumps(result))
                
                span.set_status(StatusCode.OK)
                return result
            except Exception as e:
                # Record the exception in the span
                span.record_exception(e)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Reraise the exception to ensure it's not swallowed
                raise
            # finally:
            #     # End the span
            #     span.end()
    return traced_method

def chat_completions_create(original_method, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "service.provider": service_provider,
            "url.full": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.prompts": json.dumps(kwargs.get('messages', [])),
            "llm.stream": kwargs.get('stream'),
        }

        attributes = OpenAISpanAttributes(**span_attributes)

        if kwargs.get('temperature') is not None:
            attributes["llm.temperature"] = kwargs.get('temperature')
        if kwargs.get('top_p') is not None:
            attributes["llm.top_p"] = kwargs.get('top_p')
        if kwargs.get('user') is not None:
            attributes["llm.user"] = kwargs.get('user')

        # current_span = trace.get_current_span()

        with tracer.start_as_current_span(APIS["CHAT_COMPLETION"]["METHOD"], kind=SpanKind.CLIENT) as span:
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
                                "message": choice.message.content if choice.message and choice.message.content else "",
                                **({"content_filter_results": choice["content_filter_results"]} if "content_filter_results" in choice else {})
                            }
                            for choice in result.choices 
                        ]
                    else:
                        responses = []
                    span.set_attribute("llm.responses", json.dumps(responses))

                    if hasattr(result, 'system_fingerprint') and result.system_fingerprint is not None:
                        span.set_attribute("llm.system.fingerprint", result.system_fingerprint)

                    # Get the usage
                    if hasattr(result, 'usage') and result.usage is not None:
                        usage = result.usage
                        if usage is not None:
                            usage_dict = {
                                "prompt_tokens": result.usage.prompt_tokens,
                                "completion_tokens": usage.completion_tokens,
                                "total_tokens": usage.total_tokens
                            }
                            span.set_attribute("llm.token.counts", json.dumps(usage_dict))

                    span.set_status(StatusCode.OK)
                    return result
                else:
                    result_content = []
                    span.add_event(Event.STREAM_START.value)

                    for chunk in result:
                        # Assuming `chunk` has a structure similar to what OpenAI might return,
                        # adjust the access accordingly based on actual response structure.
                        if hasattr(chunk, 'choices') and chunk.choices is not None:
                            content = [
                                choice.delta.content if choice.delta and choice.delta.content else ""
                                for choice in chunk.choices 
                            ]
                        else:
                            content = []
                        span.add_event(Event.STREAM_OUTPUT.value, {
                            "response": "".join(content)
                        })
                        result_content.append(content[0] if len(content) > 0 else "")
                    span.add_event(Event.STREAM_END.value)
                    span.set_attribute("llm.responses", json.dumps({ "message": { "role": "assistant", "content": "".join(result_content) } }))

            except Exception as e:
                # Record the exception in the span
                span.record_exception(e)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Reraise the exception to ensure it's not swallowed
                raise
            # finally:
            #     # End the span
            #     span.end()

    # return the wrapped method
    return traced_method

def embeddings_create(original_method, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "service.provider": service_provider,
            "url.full": APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            "llm.api": APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
        }

        attributes = OpenAISpanAttributes(**span_attributes)

        if kwargs.get('encoding_format') is not None:
            attributes["llm.encoding.format"] = kwargs.get('encoding_format')
        if kwargs.get('dimensions') is not None:
            attributes["llm.dimensions"] = kwargs.get('dimensions')
        if kwargs.get('user') is not None:
            attributes["llm.user"] = kwargs.get('user')

        with tracer.start_as_current_span(APIS["EMBEDDINGS_CREATE"]["METHOD"], kind=SpanKind.CLIENT) as span:
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
            # finally:
            #     # End the span
            #     span.end()
    return traced_method