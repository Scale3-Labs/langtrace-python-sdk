import pytest
import httpx
from openai import OpenAI
from opentelemetry.trace import SpanKind, StatusCode
from langtrace_python_sdk.constants.instrumentation.common import SpanAttributes
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from langtrace_python_sdk.instrumentation.openai import OpenAIInstrumentation
from tests.utils import assert_token_count
from importlib_metadata import version as v

# Initialize OpenAI instrumentation
instrumentor = OpenAIInstrumentation()
instrumentor.instrument()

@pytest.mark.vcr()
def test_embeddings_base_url(exporter, openai_client):
    input_value = "Test input"
    kwargs = {
        "input": input_value,
        "model": "text-embedding-ada-002",
    }

    openai_client.embeddings.create(**kwargs)
    spans = exporter.get_finished_spans()
    embedding_span = spans[-1]

    attributes = embedding_span.attributes
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.openai.com/v1/"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "OpenAI"


def test_embeddings_azure_provider(exporter, monkeypatch):
    # Mock response data
    mock_response = {
        "data": [{"embedding": [0.1] * 1536, "index": 0, "object": "embedding"}],
        "model": "text-embedding-ada-002",
        "object": "list",
        "usage": {"prompt_tokens": 5, "total_tokens": 5}
    }

    # Create a mock send method for the HTTP client
    def mock_send(self, request, **kwargs):
        # Create a proper request with headers
        headers = {
            "authorization": "Bearer test_api_key",
            "content-type": "application/json",
        }
        request = httpx.Request(
            method="POST",
            url="https://your-resource.azure.openai.com/v1/embeddings",
            headers=headers,
        )

        # Create response with proper context
        return httpx.Response(
            status_code=200,
            content=b'{"data": [{"embedding": [0.1, 0.1], "index": 0, "object": "embedding"}], "model": "text-embedding-ada-002", "object": "list", "usage": {"prompt_tokens": 5, "total_tokens": 5}}',
            request=request,
            headers={"content-type": "application/json"}
        )

    # Create Azure client
    azure_client = OpenAI(
        api_key="test_api_key",
        base_url="https://your-resource.azure.openai.com/v1",
    )

    # Debug prints
    print(f"Debug - Azure client type: {type(azure_client)}")
    print(f"Debug - Azure client base_url: {azure_client.base_url}")
    print(f"Debug - Azure client _client._base_url: {azure_client._client._base_url if hasattr(azure_client, '_client') else 'No _client'}")

    # Patch the HTTP client's send method
    monkeypatch.setattr(httpx.Client, "send", mock_send)

    input_value = "Test input"
    kwargs = {
        "input": input_value,
        "model": "text-embedding-ada-002",
    }

    azure_client.embeddings.create(**kwargs)
    spans = exporter.get_finished_spans()
    embedding_span = spans[-1]

    attributes = embedding_span.attributes
    assert attributes.get(SpanAttributes.LLM_URL) == "https://your-resource.azure.openai.com/v1/"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "Azure"
