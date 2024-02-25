import json

from langtrace.trace_attributes import OpenAISpanAttributes
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from constants import SERVICE_PROVIDERS
from instrumentation.openai.lib.apis import APIS


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

        current_span = trace.get_current_span()

        with tracer.start_as_current_span(APIS["CHAT_COMPLETION"]["METHOD"], kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                  span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = original_method(*args, **kwargs)
                responses = [
                    {
                        "message": choice.message.content if choice.message and choice.message.content else "",
                        **({"content_filter_results": choice["content_filter_results"]} if "content_filter_results" in choice else {})
                    }
                    for choice in result.choices 
                ]
                span.set_attribute("llm.responses", json.dumps(responses))

                # Get the usage
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
            except Exception as e:
                # Record the exception in the span
                span.record_exception(e)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Reraise the exception to ensure it's not swallowed
                raise

    # return the wrapped method
    return traced_method
    
    
