import pytest
from unittest.mock import MagicMock, patch, call
from unittest.mock import Mock
import openai
from langtrace.trace_attributes import Event, LLMSpanAttributes
from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from dotenv import find_dotenv, load_dotenv
from opentelemetry.trace.status import StatusCode
from src.langtrace_python_sdk.instrumentation.chroma.patch import collection_patch
from src.langtrace_python_sdk.instrumentation.openai.patch import chat_completions_create
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper
import importlib.metadata
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import openai

_ = load_dotenv(find_dotenv())
def capital_case(x):
    return x.capitalize()
def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'
@pytest.fixture
def openai_mock():
    with patch('openai.chat.completions.create') as mock_chat_completion:
        mock_chat_completion.return_value = {"choices": [{"text": "This is a test. This is test. This is a test."}]}
        yield mock_chat_completion

def test_completion():
        from langtrace_python_sdk import langtrace
        exporter = langtrace.init(None, None, False, False, False, True)
        openai.OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
        )
        spans = exporter.get_finished_spans()
        open_ai_span = spans[0]
        attributes = open_ai_span.attributes
        print("here...")
        print(open_ai_span.attributes)
        service_provider = 'openai'
        
        # attributes = OpenAISpanAttributes(**span_attributes)
        other_fields = ['langtrace.service.name', 'langtrace.service.type', 'langtrace.service.version', 'langtrace.version', 'url.full', 'llm.api', 'llm.model', 'llm.prompts', 'llm.stream', 'llm.responses', 'llm.token.counts']
        optional_fields = ['llm.temperature', 'llm.top_p', 'llm.user', 'llm.system.fingerprint', 'http.max.retries', 'http.timeout', 'llm.responses', 'llm.token.counts', 'llm.encoding.format', 'llm.dimensions']
        # assert len(spans) == 0
        for key in open_ai_span.attributes:
            try:
                print(key, other_fields.index(key))
                assert(key, other_fields.index(key))
            except KeyError:
                print(f"Attribute '{key}' not found in open_ai_span.attributes")
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": '1.12.0',
            "langtrace.version": "1.0.0",
            "url.full": 'chat/completions/create',
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": 'gpt-4',
            "llm.prompts": '[{"role": "user", "content": "Say this is a test three times"}]',
            "llm.stream": False,
        }
        attributes = LLMSpanAttributes(**span_attributes)
        for key, value in attributes.model_dump(by_alias=True).items():
                try:
                    if key not in optional_fields:
                        assert(key, open_ai_span.attributes.get(key) == value)
                except KeyError:
                    # Handle the KeyError (attribute not found in open_ai_span.attributes)
                    print(f"Attribute '{key}' not found in open_ai_span.attributes")
import unittest

class TestChromaPatch(unittest.TestCase):
   # Inside your TestChromaPatch class's setUp method:
    def setUp(self):
        self.tracer = Mock()
        self.span = Mock()

        # Create a context manager mock for start_as_current_span
        context_manager_mock = MagicMock()
        context_manager_mock.__enter__.return_value = self.span
        self.tracer.start_as_current_span.return_value = context_manager_mock

        self.wrapped_method = Mock(return_value="mocked method result")
        self.instance = Mock()
        self.instance.name = "aa"  # Set a valid string value

    def test_collection_patch_success(self):
        # Patching the method
        traced_method = collection_patch("ADD", "1.2.3", self.tracer)

        # Calling the patched method
        result = traced_method(self.wrapped_method, self.instance, (), {})

        # Asserting the result of the original method is returned
        self.assertEqual(result, "mocked method result")

        # Asserting the span is started with the correct parameters
        self.tracer.start_as_current_span.assert_called_once_with("chromadb.collection.add", kind=SpanKind.CLIENT)

        # Verifying span attributes are set as expected
        expected_attributes = {
            'langtrace.service.name': 'Chroma',
            'langtrace.service.type': 'vectordb',
            'langtrace.service.version': '1.2.3',
            'langtrace.version': '1.0.0',
            'db.system': 'chromadb',
            'db.operation': 'add',
            'db.collection.name': 'aa',
        }
        for key, value in expected_attributes.items():
            self.span.set_attribute.assert_has_calls([call(key, value)], any_order=True)
        # Asserting the span status is set to OK
        # self.span.set_status.assert_called_with(StatusCode.OK)


