"""
Pinecone instrumentation
"""

import importlib.metadata
from typing import Collection

import pinecone
from langtrace.trace_attributes import PineconeMethods
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.constants.instrumentation.pinecone import APIS
from langtrace_python_sdk.instrumentation.pinecone.patch import generic_patch


class PineconeInstrumentation(BaseInstrumentor):
    """
    The PineconeInstrumentation class represents the Pinecone instrumentation"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["pinecone-client >= 3.1.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version('pinecone-client')
        for operation_name, details in APIS.items():
            method_ref = details["METHOD"]
            method = None
            if method_ref is PineconeMethods.UPSERT.value:
                method = pinecone.Index.upsert
            elif method_ref is PineconeMethods.QUERY.value:
                method = pinecone.Index.query
            elif method_ref is PineconeMethods.DELETE.value:
                method = pinecone.Index.delete
            operation = details["OPERATION"]

            # Dynamically creating the patching call
            wrap_function_wrapper(
                'pinecone.data.index',
                f'Index.{operation}',
                generic_patch(method, operation_name,
                              version, tracer)
            )

    def _uninstrument(self, **kwargs):
        pass
