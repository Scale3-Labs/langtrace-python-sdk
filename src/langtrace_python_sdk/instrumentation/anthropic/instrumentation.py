"""
Instrumentation for Anthropic
"""
import importlib.metadata
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.anthropic.patch import \
    messages_create


class AnthropicInstrumentation(BaseInstrumentor):
    """
    The AnthropicInstrumentation class represents the Anthropic instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["anthropic >= 0.19.1"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version('anthropic')

        wrap_function_wrapper(
            'anthropic.resources.messages',
            'Messages.create',
            messages_create(
                'anthropic.messages.create', version, tracer)
        )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
