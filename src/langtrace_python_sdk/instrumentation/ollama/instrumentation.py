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

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W
from typing import Collection
from importlib_metadata import version as v
from langtrace_python_sdk.constants.instrumentation.ollama import APIS
from .patch import generic_patch, ageneric_patch


class OllamaInstrumentor(BaseInstrumentor):
    """
    The OllamaInstrumentor class represents the Ollama instrumentation"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["ollama >= 0.2.0, < 1"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("ollama")
        for operation_name, details in APIS.items():
            operation = details["METHOD"]
            # Dynamically creating the patching call
            _W(
                "ollama._client",
                f"Client.{operation}",
                generic_patch(operation_name, version, tracer),
            )

            _W(
                "ollama._client",
                f"AsyncClient.{operation}",
                ageneric_patch(operation_name, version, tracer),
            )
            _W(
                "ollama",
                f"{operation}",
                generic_patch(operation_name, version, tracer),
            )

    def _uninstrument(self, **kwargs):
        pass
