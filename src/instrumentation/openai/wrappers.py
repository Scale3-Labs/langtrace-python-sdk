from instrumentation.openai.lib.span_attributes import OpenAISpanAttributes
from opentelemetry.trace import Span, SpanKind

class Wrapper:
    def _with_tracer_wrapper(func):
        def _with_tracer(tracer):
            def wrapper(wrapped, instance, args, kwargs):
                return func(tracer, wrapped, instance, args, kwargs)
            return wrapper
        return _with_tracer


    @_with_tracer_wrapper
    def completion_wrapper(tracer, wrapped, instance, args, kwargs):
     

        # span needs to be opened and closed manually because the response is a generator
        span = tracer.start_span(
            "OpenAI",
            kind=SpanKind.CLIENT,
            # attributes={SpanAttributes.LLM_REQUEST_TYPE: LLM_REQUEST_TYPE.value},
        )

        url_full = "https://api.openai.com/v1/chat/completions"
        llm_api = "chat.completions.create"
        llm_model = "chat_gpt"
        llm_prompts = "prompt" 
        llm_responses = "response"
        spanatttributes = OpenAISpanAttributes(url_full = url_full , llm_api= llm_api, llm_model = llm_model , llm_prompts = llm_prompts, llm_responses = llm_responses)
        for key, value in spanatttributes.dict().items():
            span.set_attribute(key, value)
        print("created instance")
          
        response = wrapped(*args, **kwargs)
        span.end()
        return response