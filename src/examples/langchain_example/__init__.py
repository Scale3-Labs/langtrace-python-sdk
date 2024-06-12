from .basic import basic_app, rag, load_and_split
from langtrace_python_sdk import with_langtrace_root_span


class LangChainRunner:
    @with_langtrace_root_span("LangChain")
    def run(self):
        basic_app()
        rag()
        load_and_split()
