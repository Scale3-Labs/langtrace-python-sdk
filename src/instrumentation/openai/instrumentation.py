from typing import Collection

import openai
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from instrumentation.openai.patch import (chat_completions_create,
                                          embeddings_create, images_generate)


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
        wrap_function_wrapper(
            'openai.resources.images.generate',
            'Images.generate',
            images_generate(openai.images.generate, tracer)
        )
        wrap_function_wrapper(
            'openai.resources.embeddings',
            'Embeddings.create',
            embeddings_create(openai.embeddings.create, tracer)
        )

        # # simple implementation
        # def trace_openai_create(wrapped, instance, args, kwargs):
        #     with tracer.start_as_current_span("OpenAI Chat Completions Create"):
        #         return wrapped(*args, **kwargs)

        # # Applying the wrapper
        # wrap_function_wrapper('openai.resources.chat.completions', 'Completions.create', trace_openai_create)

    def _uninstrument(self, **kwargs):
        print(kwargs)

