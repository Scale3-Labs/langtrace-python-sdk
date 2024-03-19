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



class TestChatCompletion():
    data = {
        "id": "chatcmpl-93wIW4A2r0YjlDvx7PKvHV0VxbprP",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "logprobs": None,
                "message": {
                    "content": "This is a test, this is a test, this is a test.",
                    "role": "assistant",
                    "function_call": None,
                    "tool_calls": None
                }
            }
        ],
        "created": 1710726108,
        "model": "gpt-4-0613",
        "object": "chat.completion",
        "system_fingerprint": None,
        "usage": {
            "completion_tokens": 15,
            "prompt_tokens": 14,
            "total_tokens": 29
        }
    }

    @pytest.fixture
    def openai_mock(self):
        with patch('openai.chat.completions.create') as mock_chat_completion:
            mock_chat_completion.return_value = json.dumps(self.data)  # Modify this line
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

    def test_chat_completions_create_non_streaming(self, set_up_tracer, openai_mock):
    
        version = importlib.metadata.version('openai')
        wrapped_method = Mock(return_value="mocked method result")
        instance = Mock()
        instance.name = "aa"
        llm_model_value = 'gpt-4'
        messages_value = [{'role': 'user', 'content': 'Say this is a test three times'}]

        kwargs = {
                'model': llm_model_value,
                'messages': messages_value,
                'stream': False,
        }
        wrapped_function = chat_completions_create(openai.chat.completions.create, version, self.tracer)
        result = wrapped_function(wrapped_method, instance, (), kwargs)
        assert self.tracer.start_as_current_span("openai.chat.completions.create", kind=SpanKind.CLIENT)
        # Assert span attributes     
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
        
        assert self.span.set_attribute.has_calls([call(key, value) for key, value in expected_attributes.items()], any_order=True)
        # Assert span status
        assert self.span.set_status.call_count == 1
        assert self.span.set_status.has_calls([call(Status(StatusCode.OK))])
        
        # Assert reult keys
        expected_result = ['id', 'choices', 'created', 'model', 'system_fingerprint','object', 'usage']
        result_keys = json.loads(result).keys()
        assert set(expected_result) == set(result_keys), "Keys mismatch"
        
        # Assert message content
        expected_content = "This is a test, this is a test, this is a test."
   
        assert json.loads(result).get('choices')[0].get('message').get('content') == expected_content, "Content mismatch"

