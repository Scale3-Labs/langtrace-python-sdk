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
    "DELETE_ONE": {
        "METHOD": PineconeMethods.DELETE_ONE.value,
        "ENDPOINT": "/vectors/delete",
        "OPERATION": "delete",
    },
    "DELETE_MANY": {
        "METHOD": PineconeMethods.DELETE_MANY.value,
        "ENDPOINT": "/vectors/delete",
        "OPERATION": "delete",
    },
    "DELETE_ALL": {
        "METHOD": PineconeMethods.DELETE_ALL.value,
        "ENDPOINT": "/vectors/delete",
        "OPERATION": "delete",
    },
}
