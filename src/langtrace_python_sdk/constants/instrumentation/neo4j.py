from langtrace.trace_attributes import Neo4jMethods

APIS = {
    "RUN": {
        "METHOD": Neo4jMethods.RUN.value,
        "OPERATION": "run",
    },
    "BEGIN_TRANSACTION": {
        "METHOD": Neo4jMethods.BEGIN_TRANSACTION.value,
        "OPERATION": "begin_transaction",
    },
    "READ_TRANSACTION": {
        "METHOD": Neo4jMethods.READ_TRANSACTION.value,
        "OPERATION": "read_transaction",
    },
    "WRITE_TRANSACTION": {
        "METHOD": Neo4jMethods.WRITE_TRANSACTION.value,
        "OPERATION": "write_transaction",
    },
    "EXECUTE_READ": {
        "METHOD": Neo4jMethods.EXECUTE_READ.value,
        "OPERATION": "execute_read",
    },
    "EXECUTE_WRITE": {
        "METHOD": Neo4jMethods.EXECUTE_WRITE.value,
        "OPERATION": "execute_write",
    },
    "EXECUTE_QUERY": {
        "METHOD": Neo4jMethods.EXECUTE_QUERY.value,
        "OPERATION": "execute_query",
    },
    "TX_RUN": {
        "METHOD": Neo4jMethods.TX_RUN.value,
        "OPERATION": "tx_run",
    },
}