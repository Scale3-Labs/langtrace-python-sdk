from langtrace.trace_attributes import PineconeMethods

APIS = {
    "UPSERT": {
        "METHOD": PineconeMethods.UPSERT.value,
        "ENDPOINT": "/vectors/upsert",
        "OPERATION": "upsert",
    },
    "QUERY": {
        "METHOD": PineconeMethods.QUERY.value,
        "ENDPOINT": "/query",
        "OPERATION": "query",
    },
    "DELETE": {
        "METHOD": PineconeMethods.DELETE,
        "ENDPOINT": "/vectors/delete",
        "OPERATION": "delete",
    }
}
