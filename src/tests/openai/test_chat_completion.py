import unittest
from unittest.mock import MagicMock, Mock, patch, call
from langtrace_python_sdk.instrumentation.openai.patch import chat_completions_create
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_tracer
import importlib.metadata
import openai
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from opentelemetry.trace.status import Status, StatusCode
import json

class TestChatCompletion(unittest.TestCase):
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

    def setUp(self):
        self.openai_mock = patch('openai.chat.completions.create')
        self.mock_image_generate = self.openai_mock.start()
        self.mock_image_generate.return_value = json.dumps(self.data)

        # Create a tracer provider
        self.tracer = MagicMock()
        self.span = MagicMock()

        # Create a context manager mock for start_as_current_span
        context_manager_mock = MagicMock()
        context_manager_mock.__enter__.return_value = self.span
        self.tracer.start_as_current_span.return_value = context_manager_mock

    def tearDown(self):
        self.openai_mock.stop()

    def test_chat_completions_create_non_streaming(self):
        # Arrange
        version = importlib.metadata.version('openai')
        llm_model_value = 'gpt-4'
        messages_value = [{'role': 'user', 'content': 'Say this is a test three times'}]

        kwargs = {
            'model': llm_model_value,
            'messages': messages_value,
            'stream': False,
        }

        # Act
        wrapped_function = chat_completions_create(openai.chat.completions.create, version, self.tracer)
        result = wrapped_function(MagicMock(), MagicMock(), (), kwargs)

        # Assert
        self.assertTrue(self.tracer.start_as_current_span.called_once_with("openai.chat.completions.create", kind=SpanKind.CLIENT))

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
        self.assertTrue(
            self.span.set_attribute.has_calls(
                [call(key, value) for key, value in expected_attributes.items()], any_order=True
            )
        )

        self.assertEqual(self.span.set_status.call_count, 1)
        self.assertTrue(self.span.set_status.has_calls([call(Status(StatusCode.OK))]))

        expected_result = ['id', 'choices', 'created', 'model', 'system_fingerprint', 'object', 'usage']
        result_keys = json.loads(result).keys()
        self.assertSetEqual(set(expected_result), set(result_keys), "Keys mismatch")

        expected_content = "This is a test, this is a test, this is a test."
        self.assertEqual(
            json.loads(result).get('choices')[0].get('message').get('content'), expected_content, "Content mismatch"
        )

if __name__ == '__main__':
    unittest.main()