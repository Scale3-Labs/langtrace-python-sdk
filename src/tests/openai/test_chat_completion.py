import importlib.metadata
import json
import unittest
from unittest.mock import MagicMock, call

from langtrace_python_sdk.constants.instrumentation.openai import APIS
from langtrace_python_sdk.instrumentation.openai.patch import (
    chat_completions_create,
)
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from tests.utils import common_setup


class TestChatCompletion(unittest.TestCase):
    data = {
        "id": "chatcmpl-93wIW4A2r0YjlDvx7PKvHV0VxbprP",
        "choices": [
            MagicMock(
                finish_reason="stop",
                index=0,
                logprobs=None,
                message=MagicMock(
                    content="This is a test, this is a test, this is a test.",
                    role="assistant",
                    function_call=None,
                    tool_calls=None,
                ),
            )
        ],
        "created": 1710726108,
        "model": "gpt-4-0613",
        "object": "chat.completion",
        "system_fingerprint": None,
        "usage": MagicMock(
            prompt_tokens=14, completion_tokens=15, total_tokens=29
        ),
    }

    def setUp(self):
        self.openai_mock, self.tracer, self.span = common_setup(
            self.data, None
        )

    def tearDown(self):
        pass

    def test_chat_completions_create_non_streaming(self):
        # Arrange
        version = importlib.metadata.version("openai")
        llm_model_value = "gpt-4"
        messages_value = [
            {"role": "user", "content": "Say this is a test three times"}
        ]

        kwargs = {
            "model": llm_model_value,
            "messages": messages_value,
            "stream": False,
        }

        # Act
        wrapped_function = chat_completions_create(
            self.openai_mock, version, self.tracer
        )
        result = wrapped_function(MagicMock(), MagicMock(), (), kwargs)

        # Assert
        self.assertTrue(
            self.tracer.start_as_current_span.called_once_with(
                "openai.chat.completions.create", kind=SpanKind.CLIENT
            )
        )

        expected_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": "OpenAI",
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": "chat/completions/create",
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": json.dumps(kwargs.get("messages", [])),
            "llm.stream": kwargs.get("stream"),
        }
        self.assertTrue(
            self.span.set_attribute.has_calls(
                [
                    call(key, value)
                    for key, value in expected_attributes.items()
                ],
                any_order=True,
            )
        )

        self.assertTrue(
            self.span.set_status.has_calls([call(Status(StatusCode.OK))])
        )

        expected_result_data = {"model": "gpt-4-0613"}

        self.assertEqual(result.model, expected_result_data["model"])


if __name__ == "__main__":
    unittest.main()
