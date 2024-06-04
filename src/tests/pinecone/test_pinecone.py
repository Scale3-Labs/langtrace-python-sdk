import pytest
import json
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.pinecone import APIS
from importlib_metadata import version as v


def create_embedding(openai_client):
    result = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input="Some random text string goes here",
        encoding_format="float",
    )
    return result.data[0].embedding


@pytest.mark.vcr()
def test_upsert(openai_client, pinecone_client, exporter):
    embedding = create_embedding(openai_client)
    unique_id = "unique_random_id"
    data_to_upsert = {
        "id": unique_id,
        "values": embedding,
        "metadata": {"random": "random"},
    }
    index = pinecone_client.Index("test-index")
    index.upsert(vectors=[data_to_upsert], namespace="test-namespace")
    spans = exporter.get_finished_spans()
    pinecone_span = spans[-1]

    assert pinecone_span.name == APIS["UPSERT"]["METHOD"]
    attributes = pinecone_span.attributes

    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == SERVICE_PROVIDERS["PINECONE"]
    assert attributes.get("langtrace.service.type") == "vectordb"
    assert attributes.get("langtrace.service.version") == v("pinecone-client")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("db.system") == "pinecone"
    assert attributes.get("db.operation") == APIS["UPSERT"]["OPERATION"]


@pytest.mark.vcr()
def test_query(openai_client, pinecone_client, exporter):
    embedding = create_embedding(openai_client)
    unique_id = "unique_random_id"
    data_to_upsert = {
        "id": unique_id,
        "values": embedding,
        "metadata": {"random": "random"},
    }
    index = pinecone_client.Index("test-index")
    index.upsert(vectors=[data_to_upsert], namespace="test-namespace")
    filter = {"random": "random"}
    res = index.query(
        vector=embedding,
        top_k=3,
        include_values=True,
        namespace="test-namespace",
        include_metadata=True,
        filter=filter,
    )
    spans = exporter.get_finished_spans()
    query_span = spans[-1]
    assert query_span.name == APIS["QUERY"]["METHOD"]
    attributes = query_span.attributes
    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == SERVICE_PROVIDERS["PINECONE"]
    assert attributes.get("langtrace.service.type") == "vectordb"
    assert attributes.get("langtrace.service.version") == v("pinecone-client")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("db.system") == "pinecone"
    assert attributes.get("db.operation") == APIS["QUERY"]["OPERATION"]
    assert attributes.get("db.query.top_k") == 3
    assert attributes.get("db.query.namespace") == "test-namespace"
    assert attributes.get("db.query.include_values") is True
    assert attributes.get("db.query.include_metadata") is True
    assert attributes.get("db.query.usage.read_units") == 6
    assert json.loads(attributes.get("db.query.filter")) == filter
    res_matches = res.matches
    events = query_span.events
    assert len(res_matches) == len(events)
    for idx, event in enumerate(events):
        assert event.name == "db.query.match"
        attrs = event.attributes
        assert attrs.get("db.query.match.id") == res_matches[idx].id
        assert attrs.get("db.query.match.score") == res_matches[idx].score
