import pytest
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from tests.utils import assert_token_count
from importlib_metadata import version as v
from langtrace.trace_attributes import SpanAttributes


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


@pytest.mark.vcr()
def test_embeddings_azure_provider(exporter):
    # Create a new OpenAI client configured for Azure
    from openai import OpenAI
    azure_client = OpenAI(
        api_key="test_api_key",
        base_url="https://your-resource.azure.openai.com/v1",
    )

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
