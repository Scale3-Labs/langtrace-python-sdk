import importlib.metadata
import unittest
from unittest.mock import MagicMock, call

from langtrace_python_sdk.instrumentation.langchain_core.patch import generic_patch, runnable_patch
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from tests.utils import common_setup


class TestGenericPatch(unittest.TestCase):
    data = {"items": "value"}

    def setUp(self):
        self.langchain_mock, self.tracer, self.span = common_setup(self.data, None)

    def tearDown(self):
        # Clean up after each test case
        pass

    def test_generic_patch(self):
        # Arrange
        method_name = "example_method"
        trace_output = False
        trace_input = True
        task = "retriever"
        args = (1, 2, 3)
        kwargs = {"key": "value"}
        version = importlib.metadata.version("langchain-core")

        # Act
        wrapped_function = generic_patch(
            "langchain_core.retrievers", task, self.tracer, version, trace_output, trace_input
        )
        result = wrapped_function(self.langchain_mock, MagicMock(), args, kwargs)

        # Assert
        self.assertTrue(self.tracer.start_as_current_span.called_once_with(method_name, kind=SpanKind.CLIENT))

        service_provider = "Langchain Core"
        expected_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "langchain.task.name": task,
        }

        self.assertTrue(
            self.span.set_attribute.has_calls(
                [call(key, value) for key, value in expected_attributes.items()], any_order=True
            )
        )

        actual_calls = self.span.set_attribute.call_args_list
        for key, value in expected_attributes.items():
            self.assertIn(call(key, value), actual_calls)

        self.assertEqual(self.span.set_status.call_count, 1)
        self.assertTrue(self.span.set_status.has_calls([call(Status(StatusCode.OK))]))

        expected_result_data = {"items": "value"}
        self.assertEqual(result.items, expected_result_data["items"])

    def test_runnable_patch(self):
        # Arrange
        method_name = "example_method"
        trace_output = False
        trace_input = True
        args = (1, 2, 3)
        kwargs = {"key": "value"}
        version = importlib.metadata.version("langchain-core")

        # Act
        wrapped_function = runnable_patch(
            "langchain_core.runnables.passthrough",
            "runnablepassthrough",
            self.tracer,
            version,
            trace_output,
            trace_input,
        )

        result = wrapped_function(self.langchain_mock, MagicMock(), args, kwargs)

        # Assert
        self.assertTrue(self.tracer.start_as_current_span.called_once_with(method_name, kind=SpanKind.CLIENT))

        service_provider = "Langchain Core"
        expected_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "langchain.task.name": "runnablepassthrough",
        }

        self.assertTrue(
            self.span.set_attribute.has_calls(
                [call(key, value) for key, value in expected_attributes.items()], any_order=True
            )
        )

        actual_calls = self.span.set_attribute.call_args_list

        for key, value in expected_attributes.items():
            self.assertIn(call(key, value), actual_calls)

        self.assertEqual(self.span.set_status.call_count, 1)
        self.assertTrue(self.span.set_status.has_calls([call(Status(StatusCode.OK))]))

        expected_result_data = {"items": "value"}

        self.assertEqual(result.items, expected_result_data["items"])


if __name__ == "__main__":
    unittest.main()
