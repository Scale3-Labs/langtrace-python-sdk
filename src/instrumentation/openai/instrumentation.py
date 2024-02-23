from typing import Collection
from openai import OpenAI 
from wrapt import wrap_function_wrapper
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import Span, SpanKind
from opentelemetry.trace.status import StatusCode
from opentelemetry.trace import get_tracer
from opentelemetry import trace
from opentelemetry.instrumentation.openai.utils import is_openai_v1
from instrumentation.openai.wrappers import Wrapper
from instrumentation.openai.lib.span_attributes import OpenAISpanAttributes
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

class OpenAIInstrumentation(BaseInstrumentor):

    def instrument(self, **kwargs):
        print(kwargs.get('tracer_provider'))
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "0.11.2", tracer_provider)
        print(kwargs.get('argument1'))
        chat_completion_wrapper = Wrapper
        wrap_function_wrapper("openai.resources.chat.completions", "Completions.create", chat_completion_wrapper.completion_wrapper(tracer))

        return super().instrument(**kwargs)
    
    def uninstrument(self, **kwargs):
        print(kwargs)
        return super().uninstrument(**kwargs)
    
    def _uninstrument(self, **kwargs):
        # Implement logic to uninstrument here
        pass

    def instrumentation_dependencies(self) -> Collection[str]:
        # Return any instrumentation dependencies here
        return []

