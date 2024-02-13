
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor



def setup_instrumentation():
    # Set up OpenTelemetry tracing
    tracer_provider = TracerProvider()

    # Use the ConsoleSpanExporter to print traces to the console
    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    # Register any automatic instrumentation and your custom OpenAI instrumentation
    instrumentor_factory = []
    instrumentor_factory._auto_instrument(tracer_provider)

    # Make sure to register the provider
    tracer_provider.register()

# Call the setup_instrumentation function to set up instrumentation
setup_instrumentation()