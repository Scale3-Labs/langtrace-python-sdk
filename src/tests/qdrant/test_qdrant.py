from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from qdrant_client.models import PointStruct, Distance, VectorParams
import importlib


COLLECTION_NAME = "test_collection"
EMBEDDING_DIM = 4


def test_qdrant_upsert(qdrant_client, exporter):
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.DOT),
    )

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=[
            PointStruct(
                id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}
            ),
            PointStruct(
                id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}
            ),
            PointStruct(
                id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}
            ),
            PointStruct(
                id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}
            ),
            PointStruct(
                id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}
            ),
            PointStruct(
                id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}
            ),
        ],
    )
    spans = exporter.get_finished_spans()
    upsert_span = spans[0]
    attributes = upsert_span.attributes
    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == SERVICE_PROVIDERS["QDRANT"]
    assert attributes.get("langtrace.service.type") == "vectordb"
    assert attributes.get("langtrace.service.version") == importlib.metadata.version(
        "qdrant_client"
    )
    assert attributes.get("db.system") == SERVICE_PROVIDERS["QDRANT"].lower()
    assert attributes.get("db.operation") == "upsert"
    assert attributes.get("db.upsert.points_count") == 6
    assert attributes.get("db.collection.name") == COLLECTION_NAME


def test_qdrant_search(qdrant_client, exporter):
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.DOT),
    )

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=[
            PointStruct(
                id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}
            ),
            PointStruct(
                id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}
            ),
            PointStruct(
                id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}
            ),
            PointStruct(
                id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}
            ),
            PointStruct(
                id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}
            ),
            PointStruct(
                id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}
            ),
        ],
    )
    qdrant_client.search(
        collection_name=COLLECTION_NAME, query_vector=[0.2, 0.1, 0.9, 0.7], limit=3
    )

    spans = exporter.get_finished_spans()
    search_span = spans[-1]
    attributes = search_span.attributes
    assert attributes.get("db.operation") == "search"
