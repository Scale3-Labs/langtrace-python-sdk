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
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.groq.patch import (
    async_chat_completions_create,
    chat_completions_create,
)

logging.basicConfig(level=logging.FATAL)


class GroqInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["groq >= 0.5.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("groq")

        wrap_function_wrapper(
            "groq.resources.chat.completions",
            "Completions.create",
            chat_completions_create("groq.chat.completions.create", version, tracer),
        )

        wrap_function_wrapper(
            "groq.resources.chat.completions",
            "AsyncCompletions.create",
            async_chat_completions_create(
                "groq.chat.completions.create_stream", version, tracer
            ),
        )

    def _uninstrument(self, **kwargs):
        pass
