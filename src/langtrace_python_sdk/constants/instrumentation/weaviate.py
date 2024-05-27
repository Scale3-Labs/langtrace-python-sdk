from langtrace.trace_attributes import WeaviateMethods

APIS = {
    "weaviate.query.bm25": {
        "METHOD": WeaviateMethods.QUERY_BM25.value,
        "OPERATION": "query",
    },
    "weaviate.query.fetch_object_by_id": {
        "METHOD": WeaviateMethods.QUERY_FETCH_OBJECT_BY_ID.value,
        "OPERATION": "query",
    },
    "weaviate.query.fetch_objects": {
        "METHOD": WeaviateMethods.QUERY_FETCH_OBJECTS.value,
        "OPERATION": "query",
    },
    "weaviate.query.hybrid": {
        "METHOD": WeaviateMethods.QUERY_HYBRID.value,
        "OPERATION": "query",
    },
    "weaviate.query.near_object": {
        "METHOD": WeaviateMethods.QUERY_NEAR_OBJECT.value,
        "OPERATION": "query",
    },
    "weaviate.query.near_text": {
        "METHOD": WeaviateMethods.QUERY_NEAR_TEXT.value,
        "OPERATION": "query",
    },
    "weaviate.query.near_vector": {
        "METHOD": WeaviateMethods.QUERY_NEAR_VECTOR.value,
        "OPERATION": "query",
    },
    "weaviate.collections.create": {
        "METHOD": WeaviateMethods.COLLECTIONS_CREATE.value,
        "OPERATION": "create",
    },
}
