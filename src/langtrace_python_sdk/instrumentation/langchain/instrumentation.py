"""
Instrumentation for langchain.
"""
import importlib.metadata
import inspect
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.langchain.patch import generic_patch


def patch_module_classes(module_name, tracer, version, task, trace_output=True, trace_input=True):
    """
    Generic function to patch all public methods of all classes in a given module.

    Parameters:
    - module: The module object containing the classes to patch.
    - module_name: The name of the module, used in the prefix for `wrap_function_wrapper`.
    - tracer: The tracer object used in `generic_patch`.
    - version: The version parameter used in `generic_patch`.
    - task: The name used to identify the type of task in `generic_patch`.
    - exclude_private: Whether to exclude private methods (those starting with '_').
    - trace_output: Whether to trace the output of the patched methods.
    - trace_input: Whether to trace the input of the patched methods.
    """
    # import the module
    module = importlib.import_module(module_name)
    # loop through all public classes in the module
    for name, obj in inspect.getmembers(module, lambda member: inspect.isclass(member) and
                                        member.__module__ == module.__name__):
        # loop through all public methods of the class
        for method_name, _ in inspect.getmembers(obj, predicate=inspect.isfunction):
            # Skip private methods
            if method_name.startswith('_'):
                continue
            try:
                method_path = f'{name}.{method_name}'
                wrap_function_wrapper(
                    module_name,
                    method_path,
                    generic_patch(
                        method_path, task, tracer, version, trace_output, trace_input)
                )
            # pylint: disable=broad-except
            except Exception:
                pass


class LangchainInstrumentation(BaseInstrumentor):
    """
    Instrumentor for langchain.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["langchain >= 0.1.9"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version('langchain')

        modules_to_patch = [
            ('langchain.text_splitter', 'split_text', True, True),
        ]

        for module_name, task, trace_output, trace_input in modules_to_patch:
            patch_module_classes(module_name, tracer, version,
                                 task, trace_output, trace_input)

    def _uninstrument(self, **kwargs):
        pass
