"""
Instrumentation for Cohere
"""

import importlib.metadata
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.cohere.patch import (
    chat_create,
    chat_stream,
    embed_create
)

class CohereInstrumentation(BaseInstrumentor):
    """
    The CohereInstrumentation class represents the Anthropic instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["cohere >= 5.0.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("cohere")

        wrap_function_wrapper(
            "cohere.client",
            "Client.chat",
            chat_create("cohere.client.chat", version, tracer),
        )

        wrap_function_wrapper(
            "cohere.client",
            "Client.chat_stream",
            chat_stream("cohere.client.chat_stream", version, tracer),
        )

        wrap_function_wrapper(
            "cohere.client",
            "Client.embed",
            embed_create("cohere.client.embed", version, tracer),
        )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
