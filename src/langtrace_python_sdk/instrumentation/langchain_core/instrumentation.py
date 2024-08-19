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

from langtrace_python_sdk.instrumentation.langchain_core.patch import (
    generic_patch,
    runnable_patch,
)


# pylint: disable=dangerous-default-value
def patch_module_classes(
    module_name,
    tracer,
    version,
    task,
    patch_method,
    exclude_methods=[],
    exclude_classes=[],
    trace_output=True,
    trace_input=True,
):
    """
    Generic function to patch all public methods of all classes in a given module.

    Parameters:
    - module: The module object containing the classes to patch.
    - module_name: The name of the module, used in the prefix for `wrap_function_wrapper`.
    - tracer: The tracer object used in `generic_patch`.
    - version: The version parameter used in `generic_patch`.
    - task: The name used to identify the type of task in `generic_patch`.
    - patch_method: The patch method to use.
    - exclude_methods: A list of methods to exclude from patching.
    - exclude_classes: A list of classes to exclude from patching.
    - trace_output: Whether to trace the output of the patched methods.
    - trace_input: Whether to trace the input of the patched methods.
    """
    # import the module
    module = importlib.import_module(module_name)
    # loop through all public classes in the module
    for name, obj in inspect.getmembers(
        module,
        lambda member: inspect.isclass(member) and member.__module__ == module.__name__,
    ):
        # Skip private classes
        if name.startswith("_") or name in exclude_classes:
            continue
        # loop through all public methods of the class
        for method_name, method in inspect.getmembers(
            obj, predicate=inspect.isfunction
        ):
            if (
                method_name in exclude_methods
                or method.__qualname__.split(".")[0] != name
                or method_name.startswith("_")
            ):
                continue
            try:
                method_path = f"{name}.{method_name}"
                wrap_function_wrapper(
                    module_name,
                    method_path,
                    patch_method(
                        method_path, task, tracer, version, trace_output, trace_input
                    ),
                )
            # pylint: disable=broad-except
            except Exception:
                pass


class LangchainCoreInstrumentation(BaseInstrumentor):
    """
    Instrumentor for langchain.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["langchain-core >= 0.1.27"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("langchain-core")

        exclude_methods = [
            "get_name",
            "get_output_schema",
            "get_input_schema",
            "get_graph",
            "to_json",
            "to_json_not_implemented",
            "bind",
            "dict",
            "format",
            "format_messages",
            "format_prompt",
            "__or__",
            "__init__",
            "__repr__",
        ]
        exclude_classes = [
            "BaseChatPromptTemplate",
            "Runnable",
            "RunnableBinding",
            "RunnableBindingBase",
            "RunnableEach",
            "RunnableEachBase",
            "RunnableGenerator",
            "RunnablePick",
            "RunnableMap",
            "RunnableSerializable",
        ]

        modules_to_patch = [
            ("langchain_core.retrievers", "retriever", generic_patch, True, True),
            ("langchain_core.prompts.chat", "prompt", generic_patch, True, True),
            (
                "langchain_core.language_models.llms",
                "generate",
                generic_patch,
                True,
                True,
            ),
            ("langchain_core.runnables.base", "runnable", runnable_patch, True, True),
            (
                "langchain_core.runnables.passthrough",
                "runnablepassthrough",
                runnable_patch,
                True,
                True,
            ),
            (
                "langchain_core.output_parsers.string",
                "stroutputparser",
                runnable_patch,
                True,
                True,
            ),
            (
                "langchain_core.output_parsers.json",
                "jsonoutputparser",
                runnable_patch,
                True,
                True,
            ),
            (
                "langchain_core.output_parsers.list",
                "listoutputparser",
                runnable_patch,
                True,
                True,
            ),
            (
                "langchain_core.output_parsers.xml",
                "xmloutputparser",
                runnable_patch,
                True,
                True,
            ),
        ]

        for (
            module_name,
            task,
            patch_method,
            trace_output,
            trace_input,
        ) in modules_to_patch:
            patch_module_classes(
                module_name,
                tracer,
                version,
                task,
                patch_method,
                exclude_methods,
                exclude_classes,
                trace_output,
                trace_input,
            )

    def _uninstrument(self, **kwargs):
        pass
