import pytest
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from tests.utils import assert_token_count
from importlib_metadata import version as v
from langtrace.trace_attributes import SpanAttributes
from openai import OpenAI
from openai.types.create_embedding_response import CreateEmbeddingResponse
from typing import List, Dict, Any


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
    mock_response = CreateEmbeddingResponse(
        data=[{"embedding": [0.1] * 1536, "index": 0, "object": "embedding"}],
        model="text-embedding-ada-002",
        object="list",
        usage={"prompt_tokens": 5, "total_tokens": 5}
    )

    # Create a mock create method
    def mock_create(**kwargs) -> CreateEmbeddingResponse:
        return mock_response

    # Create Azure client
    azure_client = OpenAI(
        api_key="test_api_key",
        base_url="https://your-resource.azure.openai.com/v1",
    )

    # Patch the create method
    monkeypatch.setattr(azure_client.embeddings, "create", mock_create)

    input_value = "Test input"
    kwargs = {
        "input": input_value,
        "model": "text-embedding-ada-002",
    }

    azure_client.embeddings.create(**kwargs)
    spans = exporter.get_finished_spans()
    embedding_span = spans[-1]

    attributes = embedding_span.attributes
    assert attributes.get(SpanAttributes.LLM_URL) == "https://your-resource.azure.openai.com/v1"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "Azure"
