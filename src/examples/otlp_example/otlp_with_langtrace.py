# Instructions
# 1. Run the OpenTelemetry Collector with the OTLP receiver enabled
# Create otel-config.yaml with the following content:
# receivers:
#   otlp:
#     protocols:
#       grpc:
#         endpoint: "0.0.0.0:4317"
#       http:
#         endpoint: "0.0.0.0:4318"

# exporters:
#   logging:
#     loglevel: debug

# service:
#   pipelines:
#     traces:
#       receivers: [otlp]
#       exporters: [logging]
# docker pull otel/opentelemetry-collector:latest
# docker run --rm -p 4317:4317 -p 4318:4318 -v $(pwd)/otel-config.yaml:/otel-config.yaml otel/opentelemetry-collector --config otel-config.yaml
# 2. Run the following code

from langtrace_python_sdk import langtrace
from openai import OpenAI
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


# Configure the OTLP exporter to use the correct endpoint and API key
otlp_endpoint = "http://localhost:4318/v1/traces"
otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    headers=(("Content-Type", "application/json"),))
langtrace.init(custom_remote_exporter=otlp_exporter, batch=False)


def chat_with_openai():
    client = OpenAI()
    messages = [
        {
            "role": "user",
            "content": "Hello, I'm a human.",
        },
    ]
    chat_completion = client.chat.completions.create(
        messages=messages,
        stream=False,
        model="gpt-3.5-turbo",
    )
    print(chat_completion.choices[0].message.content)


def main():
    chat_with_openai()


if __name__ == "__main__":
    main()
