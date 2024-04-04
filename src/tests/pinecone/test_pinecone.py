from unittest.mock import MagicMock, patch, call
from langtrace_python_sdk.instrumentation.pinecone.patch import generic_patch
from opentelemetry.trace import SpanKind
import importlib.metadata
import pinecone
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.pinecone import APIS
import unittest
import json
from tests.utils import common_setup


class TestPinecone(unittest.TestCase):
    data = {
    "status": "success",
    "message": "Data upserted successfully",
    "upserted_ids": [1, 2, 3]
    }
    
    def setUp(self):
        self.pinecone_mock, self.tracer, self.span = common_setup(self.data, 'pinecone.Index.upsert')


    def tearDown(self):
        self.pinecone_mock.stop()

    def test_pinecone(self):
    
       # Arrange
        version = importlib.metadata.version('pinecone-client')
        method = "UPSERT"
        vectors = [[1, 2, 3], [4, 5, 6]]

        # Act
        wrapped_function = generic_patch(pinecone.Index.upsert, method, version, self.tracer)
        result = wrapped_function(MagicMock(), MagicMock(), (vectors,), {})

        # Assert
        self.assertTrue(self.tracer.start_as_current_span.called_once_with("pinecone.data.index", kind=SpanKind.CLIENT))
        api = APIS[method]
        service_provider = SERVICE_PROVIDERS["PINECONE"]
        expected_attributes = {
            'langtrace.sdk.name': 'langtrace-python-sdk',
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "db.system": "pinecone",
            "db.operation": api["OPERATION"],
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

        expected_result = ['status', 'message', 'upserted_ids']
        result_keys = json.loads(result).keys()
        self.assertSetEqual(set(expected_result), set(result_keys), "Keys mismatch")

if __name__ == '__main__':
    unittest.main()