from typing import Collection
from importlib_metadata import version as v
from langtrace_python_sdk.constants.instrumentation.vertexai import APIS
from wrapt import wrap_function_wrapper as _W
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from .patch import patch_vertexai


class VertexAIInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ["google-cloud-aiplatform >= 1.0.0"]

    def _instrument(self, **kwargs):
        trace_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", trace_provider)
        version = v("google-cloud-aiplatform")

        for api in APIS:
            module = api.get("module")
            name = api.get("name")
            method = api.get("method")
            span_name = api.get("span_name")

            _W(
                module=module,
                name=f"{name}.{method}",
                wrapper=patch_vertexai(span_name, version, tracer),
            )

    def _uninstrument(self, **kwargs):
        pass
