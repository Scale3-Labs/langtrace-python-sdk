from langtrace_python_sdk import langtrace
from openai import OpenAI
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

service_name = "langtrace-python-ollama"
otlp_endpoint = "http://localhost:4318/v1/traces"
otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    headers=(("Content-Type", "application/json"),))
langtrace.init(custom_remote_exporter=otlp_exporter, batch=False)


def chat_with_ollama():
    # Use the OpenAI endpoint, not the Ollama API.
    base_url = "http://localhost:11434/v1"
    client = OpenAI(base_url=base_url, api_key="unused")
    messages = [
        {
            "role": "user",
            "content": "Hello, I'm a human.",
        },
    ]
    chat_completion = client.chat.completions.create(
        model="llama3", messages=messages
    )
    print(chat_completion.choices[0].message.content)


def main():
    chat_with_ollama()


if __name__ == "__main__":
    main()
