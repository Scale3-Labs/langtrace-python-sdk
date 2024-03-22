import pytest
from unittest.mock import MagicMock, Mock, patch, call
from langtrace_python_sdk.instrumentation.pinecone.patch import generic_patch
from opentelemetry.trace import SpanKind
import importlib.metadata
import openai
import pinecone
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.pinecone import APIS

import json

class TestPinecone():
    data = {
    "status": "success",
    "message": "Data upserted successfully",
    "upserted_ids": [1, 2, 3]
  }


    @pytest.fixture
    def pinecone_mock(self):
        with patch('pinecone.Index.upsert') as mock_pinecone_upsert:
            mock_pinecone_upsert.return_value = json.dumps(self.data)  
            yield mock_pinecone_upsert
        

    @pytest.fixture
    def set_up(self):
        # Create a tracer provider
        self.tracer = Mock()
        self.span = Mock()

        # Create a context manager mock for start_as_current_span
        context_manager_mock = MagicMock()
        context_manager_mock.__enter__.return_value = self.span
        self.tracer.start_as_current_span.return_value = context_manager_mock
        

    def test_pinecone(self, set_up, pinecone_mock):
    
        version = importlib.metadata.version('pinecone-client')
        wrapped_method = Mock(return_value="mocked method result")
        instance = Mock()
        method = "UPSERT"      
        vectors = [[1, 2, 3], [4, 5, 6]]
        wrapped_function = generic_patch(pinecone.Index.upsert, "UPSERT", version, self.tracer)
        result = wrapped_function(wrapped_method, instance, (vectors,), {})
        assert self.tracer.start_as_current_span("pinecone.data.index", kind=SpanKind.CLIENT)
        print("Result: ")
        print(result)
        # Assert span attributes  
        api = APIS[method]
        service_provider = SERVICE_PROVIDERS["PINECONE"]   
        expected_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "db.system": "pinecone",
            "db.operation": api["OPERATION"],
        }

        
        assert self.span.set_attribute.has_calls([call(key, value) for key, value in expected_attributes.items()], any_order=True)
        # Assert span status
        assert self.span.set_status.call_count == 1
        assert self.span.set_status.has_calls([call(Status(StatusCode.OK))])
        
        # # Assert reult keys
        print("Result: ")
        print(result)
        expected_result = ['status', 'message', 'upserted_ids']
        result_keys = json.loads(result).keys()
        assert set(expected_result) == set(result_keys), "Keys mismatch"
        
