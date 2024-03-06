import importlib.metadata
from typing import Collection

import openai
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.openai.patch import (
    chat_completions_create, embeddings_create, images_generate)


class OpenAIInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["openai >= 0.27.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version('openai')
        wrap_function_wrapper(
            'openai.resources.chat.completions',
            'Completions.create',
            chat_completions_create(
                openai.chat.completions.create, version, tracer)
        )
        wrap_function_wrapper(
            'openai.resources.images',
            'Images.generate',
            images_generate(openai.images.generate, version, tracer)
        )
        wrap_function_wrapper(
            'openai.resources.embeddings',
            'Embeddings.create',
            embeddings_create(openai.embeddings.create,
                              version, tracer)
        )

    def _uninstrument(self, **kwargs):
        pass
