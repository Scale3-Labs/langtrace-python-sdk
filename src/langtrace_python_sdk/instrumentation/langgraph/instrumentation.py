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
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.langgraph.patch import patch_graph_methods


class LanggraphInstrumentation(BaseInstrumentor):
    """
    Instrumentor for langgraph.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["langgraph >= 0.0.39"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("langgraph")

        # List of modules to patch, with their corresponding patch names
        modules_to_patch = [
            (
                "langgraph.graph.graph",
                [
                    "add_node",
                    "add_edge",
                    "set_entry_point",
                    "set_finish_point",
                    "add_conditional_edges",
                ],
            ),
        ]

        for module_name, methods in modules_to_patch:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(
                module,
                lambda member: inspect.isclass(member)
                and member.__module__ == module.__name__,
            ):
                for method_name, _ in inspect.getmembers(
                    obj, predicate=inspect.isfunction
                ):
                    if method_name in methods:
                        module = f"{name}.{method_name}"
                        wrap_function_wrapper(
                            module_name,
                            module,
                            patch_graph_methods(module, tracer, version),
                        )

    def _uninstrument(self, **kwargs):
        pass
