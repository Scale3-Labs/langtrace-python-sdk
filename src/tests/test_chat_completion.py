import pytest
from unittest.mock import MagicMock, Mock, patch, call
from langtrace_python_sdk.instrumentation.openai.patch import chat_completions_create
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_tracer
from langtrace.trace_attributes import Event, LLMSpanAttributes
import importlib.metadata
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import openai
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

import json



def instrument():
        provider = TracerProvider()
        in_memory_exporter = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(in_memory_exporter))
        tracer = get_tracer(__name__, "", provider)
        version = importlib.metadata.version('openai')
        llm_model_value = 'gpt-4'
        # Define other required fields if any
        # For example:
        messages_value = [{'role': 'user', 'content': 'Say this is a test three times'}]

        # Create kwargs dictionary with valid values
        kwargs = {
            'model': llm_model_value,
            'messages': messages_value,
            'stream': False,  # Example value for stream, adjust as needed
            # Add other required fields with appropriate values
        }
        wrapped_function = chat_completions_create(openai.chat.completions.create, version, tracer)
        result = wrapped_function(None, (), {}, kwargs = kwargs)
        return result


print(instrument())

class TestChatCompletion():

    @pytest.fixture
    def openai_mock(self):
        with patch('openai.chat.completions.create') as mock_chat_completion:
            mock_chat_completion.return_value = {"choices": [{"text": "This is a test. This is test. This is a test."}]}
            yield mock_chat_completion

    @pytest.fixture
    def set_up_tracer(self):
        # Create a tracer provider
        self.tracer = Mock()
        self.span = Mock()

        # Create a context manager mock for start_as_current_span
        context_manager_mock = MagicMock()
        context_manager_mock.__enter__.return_value = self.span
        self.tracer.start_as_current_span.return_value = context_manager_mock
        from langtrace_python_sdk import langtrace
        self.exporter = langtrace.init(None, None, False, False, False, True)

    def test_chat_completions_create_non_streaming(self, set_up_tracer):
    
        version = importlib.metadata.version('openai')
        wrapped_method = Mock(return_value="mocked method result")
        instance = Mock()
        instance.name = "aa"
        llm_model_value = 'gpt-4'
        # Define other required fields if any
        # For example:
        messages_value = [{'role': 'user', 'content': 'Say this is a test three times'}]

            # Create kwargs dictionary with valid values
        kwargs = {
                'model': llm_model_value,
                'messages': messages_value,
                'stream': False,
        }
        wrapped_function = chat_completions_create(openai.chat.completions.create, version, self.tracer)
        result = wrapped_function(wrapped_method, instance, (), kwargs)
        print(result)
        assert self.tracer.start_as_current_span("openai.chat.completions.create", kind=SpanKind.CLIENT)
        assert self.tracer.start_as_current_span.call_count == 2
        print("here>>>")

        assert self.span.set_attribute.call_count == 3
     
        expected_attributes = {
            "langtrace.service.name": "OpenAI",
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": "chat/completions/create",
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.prompts": json.dumps(kwargs.get('messages', [])),
            "llm.stream": kwargs.get('stream'),
        }
        attributes = LLMSpanAttributes(**expected_attributes)
        optional_fields = ['llm.temperature', 'llm.top_p', 'llm.user', 'llm.system.fingerprint', 'http.max.retries', 'http.timeout', 'llm.responses', 'llm.token.counts', 'llm.encoding.format', 'llm.dimensions']

        # assert self.span.set_attribute.call_count == len(expected_attributes)
        # for key, value in expected_attributes.items():
        #     self.span.set_attribute.assert_has_calls([call(key, value)], any_order=True)



        expected_result = ['id', 'choices', 'created', 'model', 'system_fingerprint','object', 'usage']
        for key in result:
            try:
                index = expected_result.index(key)
                print(key, index)
                assert index >= 0, f"Attribute '{key}' not found in expected_result"
            except ValueError:
                print(f"Attribute '{key}' not found in expected_result")
        # Assert message content
        expected_content = "This is a test. This is test. This is a test."
   
        # assert result.choices[0].message.content == expected_content
