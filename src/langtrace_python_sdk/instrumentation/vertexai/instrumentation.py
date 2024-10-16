from typing import Collection
from importlib_metadata import version as v
from langtrace_python_sdk.constants.instrumentation.vertexai import APIS
from wrapt import wrap_function_wrapper as _W
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from .patch import patch_vertexai
from langtrace_python_sdk.utils import is_package_installed


class VertexAIInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        if is_package_installed("vertexai"):
            return ["vertexai >= 1.0.0"]

        return ["google-cloud-aiplatform >= 1.0.0"]

    def _instrument(self, **kwargs):
        trace_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", trace_provider)
        version = (
            v("vertexai")
            if is_package_installed("vertexai")
            else v("google-cloud-aiplatform")
        )

        for _, api_config in APIS.items():

            module = api_config.get("module")
            operation = api_config.get("operation")
            method = api_config.get("method")
            name = f"{method}.{operation}"

            _W(
                module=module,
                name=name,
                wrapper=patch_vertexai(name, version, tracer),
            )

    def _uninstrument(self, **kwargs):
        pass
