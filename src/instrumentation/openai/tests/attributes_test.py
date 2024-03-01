import sys
sys.path.append('src')
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import trace
from opentelemetry.sdk.trace.export import (ConsoleSpanExporter,
                                             SimpleSpanProcessor)
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from instrumentation.openai.instrumentation import OpenAIInstrumentation
from langtrace.trace_attributes import OpenAISpanAttributes


from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
_ = load_dotenv(find_dotenv())

def capital_case(x):
    return x.capitalize()

def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'


def exporter():
    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)

    provider = TracerProvider()
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    OpenAIInstrumentation().instrument()

    return exporter

def test_completion_streaming():
    export = exporter()
    client = OpenAI()
    client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    spans = export.get_finished_spans()
    #for span in spans:
    open_ai_span = spans[0]
    print(open_ai_span.attributes)
    # assert capital_case('semaphore') == 'Semaphore'
    assert [span.name for span in spans] == [
        "openai.chat.completion.create",
    ]
    assert open_ai_span.attributes.get("llm.api") == "/chat/completions"

# test_completion_streaming()

'''
def test_chat_completion():

    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)

    provider = TracerProvider()
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    instrumentation = OpenAIInstrumentation()

    client.completions.create(
        model="davinci-002",
        prompt="Tell me a joke about opentelemetry",
    )
    instrumentation.instrument()

    spans = exporter.get_finished_spans()
    print(spans)

test_chat_completion()
'''


