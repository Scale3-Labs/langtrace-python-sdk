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

from langtrace_python_sdk.constants.instrumentation.chroma import APIS
from langtrace_python_sdk.instrumentation.chroma.patch import collection_patch

logging.basicConfig(level=logging.FATAL)


class ChromaInstrumentation(BaseInstrumentor):
    """
    The ChromaInstrumentation class represents the ChromaDB instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["chromadb >= 0.4.23"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("chromadb")

        for operation, _ in APIS.items():
            wrap_function_wrapper(
                "chromadb.api.models.Collection",
                f"Collection.{operation.lower()}",
                collection_patch(operation, version, tracer),
            )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
