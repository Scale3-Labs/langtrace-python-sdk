APIS = {
    "INSERT": {
        "MODULE": "pymilvus",
        "METHOD": "MilvusClient.insert",
        "OPERATION": "insert",
        "SPAN_NAME": "Milvus Insert",
    },
    "QUERY": {
        "MODULE": "pymilvus",
        "METHOD": "MilvusClient.query",
        "OPERATION": "query",
        "SPAN_NAME": "Milvus Query",
    },
    "SEARCH": {
        "MODULE": "pymilvus",
        "METHOD": "MilvusClient.search",
        "OPERATION": "search",
        "SPAN_NAME": "Milvus Search",
    },
    "DELETE": {
        "MODULE": "pymilvus",
        "METHOD": "MilvusClient.delete",
        "OPERATION": "delete",
        "SPAN_NAME": "Milvus Delete",
    },
    "CREATE_COLLECTION": {
        "MODULE": "pymilvus",
        "METHOD": "MilvusClient.create_collection",
        "OPERATION": "create_collection",
        "SPAN_NAME": "Milvus Create Collection",
    },
    "UPSERT": {
        "MODULE": "pymilvus",
        "METHOD": "MilvusClient.upsert",
        "OPERATION": "upsert",
        "SPAN_NAME": "Milvus Upsert",
    },
}
