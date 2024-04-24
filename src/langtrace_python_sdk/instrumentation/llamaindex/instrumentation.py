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
import inspect
import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.llamaindex.patch import generic_patch

logging.basicConfig(level=logging.FATAL)


class LlamaindexInstrumentation(BaseInstrumentor):
    """
    The LlamaindexInstrumentation class represents the LlamaIndex instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["llama-index >= 0.10.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("llama-index")

        modules_to_patch = [
            ("llama_index.core.query_engine", "query", "query"),
            ("llama_index.core.retrievers", "retrieve", "retrieve_data"),
            ("llama_index.core.extractors", "extract", "extract_data"),
            ("llama_index.core.extractors", "aextract", "extract_data"),
            ("llama_index.core.readers", "load_data", "load_data"),
            ("llama_index.core.chat_engine", "chat", "chat"),
            ("llama_index.core.chat_engine", "achat", "chat"),
        ]

        for module_name, method, task in modules_to_patch:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(
                module,
                lambda member: inspect.isclass(member)
                and member.__module__.startswith(module_name),
            ):
                for method_name, _ in inspect.getmembers(
                    obj, predicate=inspect.isfunction
                ):
                    if method_name == method:
                        wrap_function_wrapper(
                            module_name,
                            ".".join([name, method_name]),
                            generic_patch(
                                f"llamaindex.{name}.{method_name}",
                                task,
                                tracer,
                                version,
                            ),
                        )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
