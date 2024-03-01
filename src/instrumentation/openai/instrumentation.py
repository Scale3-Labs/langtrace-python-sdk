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
            chat_completions_create(
                openai.chat.completions.create, openai.__version__, tracer)
        )
        wrap_function_wrapper(
            'openai.resources.images',
            'Images.generate',
            images_generate(openai.images.generate, openai.__version__, tracer)
        )
        wrap_function_wrapper(
            'openai.resources.embeddings',
            'Embeddings.create',
            embeddings_create(openai.embeddings.create,
                              openai.__version__, tracer)
        )

    def _uninstrument(self, **kwargs):
        print(kwargs)
