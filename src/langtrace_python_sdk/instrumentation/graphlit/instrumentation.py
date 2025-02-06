from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W
from typing import Collection
from importlib_metadata import version as v
from .patch import patch_graphlit_operation

class GraphlitInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["graphlit-client >= 1.0.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("graphlit-client")
        try:
            _W(
                "graphlit.graphlit",
                "Client.ingest_uri",
                patch_graphlit_operation("ingest_uri", version, tracer),
            )
            _W(
                "graphlit.graphlit",
                "Client.create_feed",
                patch_graphlit_operation("create_feed", version, tracer),
            )
            _W(
                "graphlit.graphlit",
                "Client.create_specification",
                patch_graphlit_operation("create_specification", version, tracer),
            )
            _W(
                "graphlit.graphlit",
                "Client.create_conversation",
                patch_graphlit_operation("create_conversation", version, tracer),
            )
            _W(
                "graphlit.graphlit",
                "Client.format_conversation",
                patch_graphlit_operation("format_conversation", version, tracer),
            )
            _W(
                "graphlit.graphlit",
                "Client.complete_conversation",
                patch_graphlit_operation("complete_conversation", version, tracer),
            )
            _W(
                "graphlit.graphlit",
                "Client.prompt_conversation",
                patch_graphlit_operation("prompt_conversation", version, tracer),
            )
        except Exception:
            pass

    def _uninstrument(self, **kwargs):
        pass