from typing import Collection
from openai import OpenAI 

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import Span, SpanKind
from opentelemetry.trace.status import StatusCode

from opentelemetry.instrumentation.openai.utils import is_openai_v1
from instrumentation.openai.patch import chat_completion_create

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

class OpenAIInstrumentation(BaseInstrumentor):
    
    def instrument(self, **kwargs):
        print(kwargs.get('argument1'))
        chat_completion_create()
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

