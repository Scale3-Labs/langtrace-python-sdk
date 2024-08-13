from langtrace_python_sdk import with_langtrace_root_span
from .main import run_main


class OpenAIRunner:
    @with_langtrace_root_span("OpenAI")
    def run(self):
        run_main()
