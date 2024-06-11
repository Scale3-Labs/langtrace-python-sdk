from examples.anthropic_example.completion import messages_create
from langtrace_python_sdk import with_langtrace_root_span


class AnthropicRunner:
    @with_langtrace_root_span("Anthropic")
    def run(self):
        messages_create()
