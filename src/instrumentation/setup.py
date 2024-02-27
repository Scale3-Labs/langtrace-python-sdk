
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (ConsoleSpanExporter,
                                            SimpleSpanProcessor)

from instrumentation.chroma.instrumentation import ChromaInstrumentation
from instrumentation.llamaindex.instrumentation import \
    LlamaindexInstrumentation
from instrumentation.openai.instrumentation import OpenAIInstrumentation
from instrumentation.pinecone.instrumentation import PineconeInstrumentation


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
    openai_instrumentation = OpenAIInstrumentation()
    pinecone_instrumentation = PineconeInstrumentation()
    llamaindex_instrumentation = LlamaindexInstrumentation()
    chroma_instrumentation = ChromaInstrumentation()

    # Call the instrument method with some arguments
    openai_instrumentation.instrument()
    pinecone_instrumentation.instrument()
    llamaindex_instrumentation.instrument()
    chroma_instrumentation.instrument()

    print("setup complete")
