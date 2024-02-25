
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (ConsoleSpanExporter,
                                            SimpleSpanProcessor)

from instrumentation.openai.instrumentation import OpenAIInstrumentation


def setup_instrumentation():

    # Set up OpenTelemetry tracing
    tracer_provider = TracerProvider()

    # Use the ConsoleSpanExporter to print traces to the console
    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))
    
    # Initialize tracer
    trace.set_tracer_provider(tracer_provider)

    # Initialize and enable your custom OpenAI instrumentation
    # Create an instance of OpenAIInstrumentation
    instrumentation = OpenAIInstrumentation()

    # Call the instrument method with some arguments
    instrumentation.instrument()

    print("setup complete")
