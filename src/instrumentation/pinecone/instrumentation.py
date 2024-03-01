from typing import Collection

import pinecone
from langtrace.trace_attributes import PineconeMethods
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from instrumentation.pinecone.lib.apis import APIS
from instrumentation.pinecone.patch import generic_patch


class PineconeInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["pinecone-client >= 3.1.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
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
                              pinecone.__version__, tracer)
            )

    def _uninstrument(self, **kwargs):
        print(kwargs)