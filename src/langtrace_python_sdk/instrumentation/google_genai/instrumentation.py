from typing import Collection
from importlib_metadata import version as v
from wrapt import wrap_function_wrapper as _W
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from .patch import patch_google_genai, patch_google_genai_streaming


class GoogleGenaiInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ["google-genai >= 0.1.0", "google-generativeai < 1.0.0"]

    def _instrument(self, **kwargs):
        trace_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", trace_provider)
        version = v("google-genai")

        _W(
            module="google.genai",
            name="models.Models.generate_content",
            wrapper=patch_google_genai(tracer, version),
        )
        _W(
            module="google.genai",
            name="models.Models.generate_content_stream",
            wrapper=patch_google_genai_streaming(tracer, version),
        )

    def _uninstrument(self, **kwargs):
        pass
