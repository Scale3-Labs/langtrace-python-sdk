"""
Copyright (c) 2024 Scale3 Labs
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Collection, Optional, Any
import importlib.metadata
import logging

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer, TracerProvider
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.litellm.patch import (
    async_chat_completions_create,
    async_embeddings_create,
    async_images_generate,
    chat_completions_create,
    embeddings_create,
    images_generate,
)

logging.basicConfig(level=logging.FATAL)


class LiteLLMInstrumentation(BaseInstrumentor): # type: ignore

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["litellm >= 1.48.0", "trace-attributes >= 4.0.5"]

    def _instrument(self, **kwargs: Any) -> None:
        tracer_provider: Optional[TracerProvider] = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version: str = importlib.metadata.version("openai")

        wrap_function_wrapper(
            "litellm",
            "completion",
            chat_completions_create(version, tracer),
        )

        wrap_function_wrapper(
            "litellm",
            "text_completion",
            chat_completions_create(version, tracer),
        )

        wrap_function_wrapper(
            "litellm.main",
            "acompletion",
            async_chat_completions_create(version, tracer),
        )

        wrap_function_wrapper(
            "litellm.main",
            "image_generation",
            images_generate(version, tracer),
        )

        wrap_function_wrapper(
            "litellm.main",
            "aimage_generation",
            async_images_generate(version, tracer),
        )

        wrap_function_wrapper(
            "litellm.main",
            "embedding",
            embeddings_create(version, tracer),
        )

        wrap_function_wrapper(
            "litellm.main",
            "aembedding",
            async_embeddings_create(version, tracer),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        pass
