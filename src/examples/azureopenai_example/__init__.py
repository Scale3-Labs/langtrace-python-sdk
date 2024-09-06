from examples.azureopenai_example.completion import chat_completion
from langtrace_python_sdk import with_langtrace_root_span, langtrace

langtrace.init()

class AzureOpenAIRunner:
    @with_langtrace_root_span("AzureOpenAI")
    def run(self):
        chat_completion()
