from .basic import basic_app, rag, load_and_split
from langtrace_python_sdk import with_langtrace_root_span

from .groq_example import groq_basic, groq_streaming


class LangChainRunner:
    @with_langtrace_root_span("LangChain")
    def run(self):
        basic_app()
        rag()
        load_and_split()


class GroqRunner:
    @with_langtrace_root_span("Groq")
    def run(self):
        groq_streaming()
