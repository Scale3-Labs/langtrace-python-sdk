from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer

from typing import Collection
from importlib_metadata import version as v
from wrapt import wrap_function_wrapper as _W

from langtrace_python_sdk.constants.instrumentation.milvus import APIS
from .patch import generic_patch


class MilvusInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["pymilvus >= 2.4.1"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("pymilvus")
        for api in APIS.values():
            _W(
                module=api["MODULE"],
                name=api["METHOD"],
                wrapper=generic_patch(api, version, tracer),
            )

    def _uninstrument(self, **kwargs):
        pass
