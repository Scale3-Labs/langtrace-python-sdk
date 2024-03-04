import sys
sys.path.append('src')
import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import trace
from opentelemetry.sdk.trace.export import (SimpleSpanProcessor)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from instrumentation.openai.instrumentation import OpenAIInstrumentation
from langtrace.trace_attributes import OpenAISpanAttributes
from constants import SERVICE_PROVIDERS
from instrumentation.openai.lib.apis import APIS
from dotenv import find_dotenv, load_dotenv
from unittest.mock import patch
from examples.openai.chat_completion import chat_completion


_ = load_dotenv(find_dotenv())

def capital_case(x):
    return x.capitalize()

def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'

@pytest.fixture
def exporter():
    with patch("examples.openai.setup.setup_instrumentation") as mock:
        exporter = InMemorySpanExporter()
        processor = SimpleSpanProcessor(exporter)

        provider = TracerProvider()
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        OpenAIInstrumentation().instrument()
        mock.return_value = None
        yield exporter


def test_completion(exporter):
        
        chat_completion()
                
        spans = exporter.get_finished_spans()
        open_ai_span = spans[0]
        print(open_ai_span.attributes)
        
        service_provider = SERVICE_PROVIDERS['OPENAI']
            
        span_attributes = {
                        "service.provider": service_provider,
                        "url.full": APIS["CHAT_COMPLETION"]["ENDPOINT"],
                        "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
                        "llm.model": 'gpt-4',
                        "llm.stream": False,
                        "llm.prompts":'[{"role": "user", "content": "Say this is a test three times"}]',
                    }

        attributes = OpenAISpanAttributes(**span_attributes)
        optional_fields = ['llm.responses', 'llm.token.counts']
        
        for key, value in attributes.model_dump(by_alias=True).items():
                try:
                    if key not in optional_fields:
                        assert (open_ai_span.attributes.get(key)) == (value)
                except KeyError:
                    # Handle the KeyError (attribute not found in open_ai_span.attributes)
                    print(f"Attribute '{key}' not found in open_ai_span.attributes")
         


