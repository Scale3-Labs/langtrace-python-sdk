from langtrace.trace_attributes import WeaviateMethods

APIS = {
    "weaviate.query.bm25": {
        "MODULE": WeaviateMethods.QUERY_BM25.value,
        "METHOD": "_BM25Query.bm25",
        "OPERATION": "query",
    },
    "weaviate.query.fetch_object_by_id": {
        "MODULE": WeaviateMethods.QUERY_FETCH_OBJECT_BY_ID.value,
        "METHOD": "_FetchObjectByIDQuery.fetch_object_by_id",
        "OPERATION": "query",
    },
    "weaviate.query.fetch_objects": {
        "MODULE": WeaviateMethods.QUERY_FETCH_OBJECTS.value,
        "METHOD": "_FetchObjectsQuery.fetch_objects",
        "OPERATION": "query",
    },
    "weaviate.query.hybrid": {
        "MODULE": WeaviateMethods.QUERY_HYBRID.value,
        "METHOD": "_HybridQuery.hybrid",
        "OPERATION": "query",
    },
    "weaviate.query.near_object": {
        "MODULE": WeaviateMethods.QUERY_NEAR_OBJECT.value,
        "METHOD": "_NearObjectQuery.near_object",
        "OPERATION": "query",
    },
    "weaviate.query.near_text": {
        "MODULE": WeaviateMethods.QUERY_NEAR_TEXT.value,
        "METHOD": "_NearTextQuery.near_text",
        "OPERATION": "query",
    },
    "weaviate.query.near_vector": {
        "MODULE": WeaviateMethods.QUERY_NEAR_VECTOR.value,
        "METHOD": "_NearVectorQuery.near_vector",
        "OPERATION": "query",
    },
    "weaviate.collections.create": {
        "MODULE": WeaviateMethods.COLLECTIONS_OPERATIONS.value,
        "METHOD": "_Collections.create",
        "OPERATION": "create",
    },
}
