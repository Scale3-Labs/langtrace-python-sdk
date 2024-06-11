from langtrace_python_sdk import langtrace, with_langtrace_root_span
import ollama
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

langtrace.init(write_spans_to_console=True)


@with_langtrace_root_span("Ollama")
def basic():
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": "hi",
            },
        ],
        stream=True,
    )
    print("", response)

    # return response["message"]["content"]
