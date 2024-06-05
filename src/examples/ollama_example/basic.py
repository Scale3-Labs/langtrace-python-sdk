from langtrace_python_sdk import langtrace, with_langtrace_root_span
import ollama
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

langtrace.init(
    custom_remote_exporter=ConsoleSpanExporter(),
    # write_spans_to_console=True,
    disable_instrumentations={"all_except": ["ollama"]},
)


@with_langtrace_root_span()
def basic():
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": "Why is the sky blue?",
            },
        ],
    )
    return response["message"]["content"]
