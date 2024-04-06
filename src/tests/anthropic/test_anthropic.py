import importlib.metadata
import json
import unittest
from unittest.mock import MagicMock, call

from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.instrumentation.anthropic.patch import messages_create
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from tests.utils import common_setup


class TestAnthropic(unittest.TestCase):
    data = {
        "content": [MagicMock(text="Some text", type="text")],
        "system_fingerprint": "None",
        "usage": MagicMock(input_tokens=23, output_tokens=44),
        "chunks": [MagicMock(delta="Some text", message="text")],
    }

    def setUp(self):
        # Mock the original method
        self.anthropic_mock, self.tracer, self.span = common_setup(self.data, None)

    def tearDown(self):
        pass

    def test_anthropic(self):
        # Arrange
        version = importlib.metadata.version("anthropic")
        kwargs = {
            "model": "claude-3-opus-20240229",
            "messages": [{"role": "user", "content": "How are you today?"}],
            "stream": False,
        }

        # Act
        wrapped_function = messages_create("anthropic.messages.create", version, self.tracer)
        result = wrapped_function(self.anthropic_mock, MagicMock(), (), kwargs)

        # Assert
        self.assertTrue(
            self.tracer.start_as_current_span.called_once_with("anthropic.messages.create", kind=SpanKind.CLIENT)
        )
        self.assertTrue(self.span.set_status.has_calls([call(Status(StatusCode.OK))]))

        expected_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": "Anthropic",
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": "/v1/messages",
            "llm.api": APIS["MESSAGES_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": json.dumps(kwargs.get("messages", [])),
            "llm.stream": kwargs.get("stream"),
        }

        self.assertTrue(
            self.span.set_attribute.has_calls(
                [call(key, value) for key, value in expected_attributes.items()], any_order=True
            )
        )

        expected_result_data = {"system_fingerprint": "None"}

        self.assertEqual(result.system_fingerprint, expected_result_data["system_fingerprint"])


if __name__ == "__main__":
    unittest.main()
