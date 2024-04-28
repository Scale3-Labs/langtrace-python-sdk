from langtrace.trace_attributes import QdrantDBMethods

APIS = {
    "ADD": {
        "METHOD": QdrantDBMethods.ADD.value,
        "OPERATION": "add",
    },
    "GET_COLLECTION": {
        "METHOD": QdrantDBMethods.GET_COLLECTION.value,
        "OPERATION": "get_collection",
    },
    "GET_COLLECTIONS": {
        "METHOD": QdrantDBMethods.GET_COLLECTIONS.value,
        "OPERATION": "get_collections",
    },
    "QUERY": {
        "METHOD": QdrantDBMethods.QUERY.value,
        "OPERATION": "query",
    },
    "QUERY_BATCH": {
        "METHOD": QdrantDBMethods.QUERY_BATCH.value,
        "OPERATION": "query_batch",
    },
    "DELETE": {
        "METHOD": QdrantDBMethods.DELETE.value,
        "OPERATION": "delete",
    },
    "DISCOVER": {
        "METHOD": QdrantDBMethods.DISCOVER.value,
        "OPERATION": "discover",
    },
    "DISCOVER_BATCH": {
        "METHOD": QdrantDBMethods.DISCOVER_BATCH.value,
        "OPERATION": "discover_batch",
    },
    "RECOMMEND": {
        "METHOD": QdrantDBMethods.RECOMMEND.value,
        "OPERATION": "recommend",
    },
    "RECOMMEND_BATCH": {
        "METHOD": QdrantDBMethods.RECOMMEND_BATCH.value,
        "OPERATION": "recommend_batch",
    },
    "RETRIEVE": {
        "METHOD": QdrantDBMethods.RETRIEVE.value,
        "OPERATION": "retrieve",
    },
    "SEARCH": {
        "METHOD": QdrantDBMethods.SEARCH.value,
        "OPERATION": "search",
    },
    "SEARCH_BATCH": {
        "METHOD": QdrantDBMethods.SEARCH_BATCH.value,
        "OPERATION": "search_batch",
    },
    "UPSERT": {
        "METHOD": QdrantDBMethods.UPSERT.value,
        "OPERATION": "upsert",
    },
    "COUNT": {
        "METHOD": QdrantDBMethods.COUNT.value,
        "OPERATION": "count",
    },
    "UPDATE_COLLECTION": {
        "METHOD": QdrantDBMethods.UPDATE_COLLECTION.value,
        "OPERATION": "update_collection",
    },
    "UPDATE_VECTORS": {
        "METHOD": QdrantDBMethods.UPDATE_VECTORS.value,
        "OPERATION": "update_vectors",
    },
}
