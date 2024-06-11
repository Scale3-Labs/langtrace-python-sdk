from langtrace_python_sdk import with_langtrace_root_span
from .basic import basic as basic_app


class QdrantRunner:
    @with_langtrace_root_span("Qdrant")
    def run(self):
        basic_app()
