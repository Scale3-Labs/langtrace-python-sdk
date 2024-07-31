from typing import Collection
from importlib_metadata import version as v
from langtrace_python_sdk.constants.instrumentation.gemini import APIS
from wrapt import wrap_function_wrapper as _W
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from .patch import patch_gemini, apatch_gemini


class GeminiInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ["google-generativeai >= 0.5.0"]

    def _instrument(self, **kwargs):
        trace_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", trace_provider)
        version = v("google-generativeai")

        for _, api_config in APIS.items():
            module = api_config.get("module")
            operation = api_config.get("operation")
            method = api_config.get("method")
            name = f"{method}.{operation}"

            _W(
                module=module,
                name=name,
                wrapper=(
                    apatch_gemini(name, version, tracer)
                    if operation == "generate_content_async"
                    else patch_gemini(name, version, tracer)
                ),
            )

    def _uninstrument(self, **kwargs):
        pass
