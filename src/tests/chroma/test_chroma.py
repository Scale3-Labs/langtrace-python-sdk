import importlib
from chromadb.utils import embedding_functions
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS

COLLECTION_NAME = "test_collection"


def test_chroma_add(chroma_client, exporter):
    embedder = embedding_functions.DefaultEmbeddingFunction()
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME, embedding_function=embedder
    )
    collection.add(
        documents=["This is a document", "This is another document"],
        metadatas=[{"source": "my_source"}, {"source": "my_source"}],
        ids=["id1", "id2"],
    )
    spans = exporter.get_finished_spans()
    chroma_span = spans[-1]

    attributes = chroma_span.attributes

    assert attributes.get("db.collection.name") == COLLECTION_NAME
    assert attributes.get("db.operation") == "add"
    assert attributes.get("db.system") == "chromadb"
    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == SERVICE_PROVIDERS["CHROMA"]
    assert attributes.get("langtrace.service.type") == "vectordb"
    assert attributes.get("langtrace.service.version") == importlib.metadata.version(
        "chromadb"
    )
