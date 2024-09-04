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
from typing import Collection, Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import TracerProvider
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper
from typing import Any
from langtrace_python_sdk.instrumentation.anthropic.patch import messages_create

logging.basicConfig(level=logging.FATAL)


class AnthropicInstrumentation(BaseInstrumentor):  # type: ignore[misc]
    """
    The AnthropicInstrumentation class represents the Anthropic instrumentation.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["anthropic >= 0.19.1"]

    def _instrument(self, **kwargs: dict[str, Any]) -> None:
        tracer_provider: TracerProvider = kwargs.get("tracer_provider")  # type: ignore
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("anthropic")

        wrap_function_wrapper(
            "anthropic.resources.messages",
            "Messages.create",
            messages_create(version, tracer),
        )

    def _instrument_module(self, module_name: str) -> None:
        pass

    def _uninstrument(self, **kwargs: dict[str, Any]) -> None:
        pass
