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

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Set up the tracer provider
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Set up the OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")

# Set up a span processor and add it to the tracer provider
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Create a span
with tracer.start_as_current_span("example-span"):
    print("Hello, World!")
