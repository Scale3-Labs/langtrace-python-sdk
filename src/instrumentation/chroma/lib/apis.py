from langtrace.trace_attributes import ChromaDBMethods

APIS = {
    "ADD": {
        "METHOD": ChromaDBMethods.ADD.value,
        "OPERATION": "add",
    },
    "GET": {
        "METHOD": ChromaDBMethods.GET.value,
        "OPERATION": "get",
    },
    "QUERY": {
        "METHOD": ChromaDBMethods.QUERY.value,
        "OPERATION": "query",
    },
    "DELETE": {
        "METHOD": ChromaDBMethods.DELETE.value,
        "OPERATION": "delete",
    },
    "PEEK": {
        "METHOD": ChromaDBMethods.PEEK.value,
        "OPERATION": "peek",
    },
    "UPDATE": {
        "METHOD": ChromaDBMethods.UPDATE.value,
        "OPERATION": "update",
    },
    "UPSERT": {
        "METHOD": ChromaDBMethods.UPSERT.value,
        "OPERATION": "upsert",
    },
    "MODIFY": {
        "METHOD": ChromaDBMethods.MODIFY.value,
        "OPERATION": "modify",
    },
    "COUNT": {
        "METHOD": ChromaDBMethods.COUNT.value,
        "OPERATION": "count",
    },
}
