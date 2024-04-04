from unittest.mock import MagicMock, patch, call
from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from opentelemetry.trace.status import StatusCode,Status
from langtrace_python_sdk.instrumentation.chroma.patch import collection_patch
from opentelemetry.trace import SpanKind
from tests.utils import common_setup
import unittest
import json


class TestChromaPatch(unittest.TestCase):
    data = {
        "status": "success",
    }
    def setUp(self):
            self.chroma_mock, self.tracer, self.span = common_setup(self.data, 'chromadb.Collection.add')
            self.wrapped_method = MagicMock(return_value="mocked method result")
            self.instance = MagicMock()
            self.instance.name = "aa" 

    def tearDown(self):
        self.chroma_mock.stop()

    def test_collection_patch_success(self):
        # Arrange
        traced_method = collection_patch("ADD", "1.2.3", self.tracer)

        # Act
        result = traced_method(self.wrapped_method, self.instance, (), {})

        # Assert
        # Assert the result of the original method is returned
        self.assertEqual(result, "mocked method result")

        # Assert the span is started with the correct parameters
        self.assertTrue(self.tracer.start_as_current_span.called_once_with("chromadb.Collection.add", kind=SpanKind.CLIENT))

        # Verify span attributes are set as expected
        expected_attributes = {
            'langtrace.sdk.name': 'langtrace-python-sdk',
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

        actual_calls = self.span.set_attribute.call_args_list

        for key, value in expected_attributes.items():
            self.assertIn(call(key, value), actual_calls)
        
        # Assert the span status is set to OK
        self.span.set_status.assert_called_with(StatusCode.OK)
        

if __name__ == '__main__':
    unittest.main()