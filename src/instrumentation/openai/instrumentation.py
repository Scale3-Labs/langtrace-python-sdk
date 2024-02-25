from typing import Collection

import openai
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import Span, SpanKind, get_tracer
from opentelemetry.trace.status import StatusCode
from wrapt import wrap_function_wrapper

from instrumentation.openai.patch import chat_completions_create
from instrumentation.openai.wrappers import Wrapper


class OpenAIInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["openai >= 0.27.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        wrap_function_wrapper(
            'openai.resources.chat.completions',
            'Completions.create',
            chat_completions_create(openai.chat.completions.create, tracer)
        )

        # # simple implementation
        # def trace_openai_create(wrapped, instance, args, kwargs):
        #     with tracer.start_as_current_span("OpenAI Chat Completions Create"):
        #         return wrapped(*args, **kwargs)

        # # Applying the wrapper
        # wrap_function_wrapper('openai.resources.chat.completions', 'Completions.create', trace_openai_create)

    def _uninstrument(self, **kwargs):
        print(kwargs)

