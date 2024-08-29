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

import importlib.metadata
import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W

from langtrace_python_sdk.instrumentation.mistral.patch import (
    chat_complete,
    embeddings_create,
)

logging.basicConfig(level=logging.FATAL)

class MistralInstrumentation(BaseInstrumentor):
    
    def instrumentation_dependencies(self) -> Collection[str]:
        return ["mistralai >= 1.0.1"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("mistralai")

        _W(
            module="mistralai.chat",
            name="Chat.complete",
            wrapper=chat_complete("mistral.chat.complete", version, tracer),
        )

        _W(
            module="mistralai.chat",
            name="Chat.stream",
            wrapper=chat_complete("mistral.chat.stream", version, tracer, is_streaming=True),
        )

        _W(
            module="mistralai.chat",
            name="Chat.complete_async",
            wrapper=chat_complete("mistral.chat.complete_async", version, tracer, is_async=True),
        )

        _W(
            module="mistralai.embeddings",
            name="Embeddings.create",
            wrapper=embeddings_create("mistral.embeddings.create", version, tracer),
        )

        _W(
            module="mistralai.embeddings",
            name="Embeddings.create_async",
            wrapper=embeddings_create("mistral.embeddings.create_async", version, tracer, is_async=True),
        )

    def _uninstrument(self, **kwargs):
        pass