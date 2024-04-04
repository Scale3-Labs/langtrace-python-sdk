
import unittest
from unittest.mock import MagicMock, Mock, patch, call
from langtrace_python_sdk.instrumentation.langchain_community.patch import generic_patch
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_tracer
import importlib.metadata
import openai
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from opentelemetry.trace.status import Status, StatusCode
import json
from tests.utils import common_setup
class TestGenericPatch(unittest.TestCase):
    data = {"key": "value"}
    def setUp(self):
        self.langchain_mock, self.tracer, self.span = common_setup(self.data, None)

    def tearDown(self):
        # Clean up after each test case
        pass

    def test_generic_patch(self):
        # Arrange
        method_name = "example_method"
        trace_output = False
        trace_input = False 
        args = (1, 2, 3)
        task = "vector_store"
        kwargs = {'key': 'value'}
        version = importlib.metadata.version("langchain-community")

        # Act
        wrapped_function = generic_patch("langchain_community.vectorstores.faiss", task, self.tracer, version, trace_output, trace_input)
        result = wrapped_function(self.langchain_mock, MagicMock(), args, kwargs)

        # Assert
        self.assertTrue(self.tracer.start_as_current_span.called_once_with(method_name, kind=SpanKind.CLIENT))
        
        service_provider = "Langchain Community"
        expected_attributes = {
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

        expected_result_data = {"key": "value"  }   
        self.assertEqual(result.key, expected_result_data["key"])


if __name__ == '__main__':
    unittest.main()