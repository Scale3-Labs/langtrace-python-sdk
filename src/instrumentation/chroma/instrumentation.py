import importlib.metadata
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from instrumentation.chroma.lib.apis import APIS
from instrumentation.chroma.patch import collection_patch


class ChromaInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["chromadb >= 0.4.23"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version('chromadb')

        for operation, details in APIS.items():
            wrap_function_wrapper(
                'chromadb.api.models.Collection',
                f'Collection.{operation.lower()}',
                collection_patch(operation, version, tracer)
            )

    def _instrument_module(self, module_name):
        print(module_name)

    def _uninstrument(self, **kwargs):
        print(kwargs)
