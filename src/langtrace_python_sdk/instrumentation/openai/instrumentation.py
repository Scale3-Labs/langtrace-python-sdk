import importlib.metadata
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.openai.patch import (
    async_embeddings_create,
    async_images_generate,
    chat_completions_create,
    embeddings_create,
    images_generate,
    async_chat_completions_create,
)

import logging

logging.basicConfig(level=logging.FATAL)


class OpenAIInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["openai >= 0.27.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("openai")

        wrap_function_wrapper(
            "openai.resources.chat.completions",
            "Completions.create",
            chat_completions_create("openai.chat.completions.create", version, tracer),
        )

        wrap_function_wrapper(
            "openai.resources.chat.completions",
            "AsyncCompletions.create",
            async_chat_completions_create(
                "openai.chat.completions.create_stream", version, tracer
            ),
        )

        wrap_function_wrapper(
            "openai.resources.images",
            "Images.generate",
            images_generate("openai.images.generate", version, tracer),
        )

        wrap_function_wrapper(
            "openai.resources.images",
            "AsyncImages.generate",
            async_images_generate("openai.images.generate", version, tracer),
        )
        wrap_function_wrapper(
            "openai.resources.embeddings",
            "Embeddings.create",
            embeddings_create("openai.embeddings.create", version, tracer),
        )

        wrap_function_wrapper(
            "openai.resources.embeddings",
            "AsyncEmbeddings.create",
            async_embeddings_create("openai.embeddings.create", version, tracer),
        )

    def _uninstrument(self, **kwargs):
        pass
