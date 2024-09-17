from examples.langchain_example.langchain_google_genai import basic_google_genai
from .basic import basic_app, rag, load_and_split
from langtrace_python_sdk import with_langtrace_root_span

from .groq_example import groq_basic, groq_tool_choice, groq_streaming
from .langgraph_example_tools import basic_graph_tools


class LangChainRunner:
    @with_langtrace_root_span("LangChain")
    def run(self):
        basic_app()
        rag()
        load_and_split()
        basic_graph_tools()
        basic_google_genai()


class GroqRunner:
    @with_langtrace_root_span("Groq")
    def run(self):
        groq_streaming()
        groq_basic()
        groq_tool_choice()
