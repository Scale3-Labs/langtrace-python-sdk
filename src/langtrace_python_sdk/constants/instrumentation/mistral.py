from langtrace.trace_attributes import MistralMethods

APIS = {
    "CHAT_COMPLETE": {
        "METHOD": MistralMethods.CHAT_COMPLETE.value,
        "ENDPOINT": "/v1/chat/completions",
    },
    "ASYNC_CHAT_COMPLETE": {
        "METHOD": MistralMethods.ASYNC_CHAT_COMPLETE.value,
        "ENDPOINT": "/v1/chat/completions",
    },
    "CHAT_STREAM": {
        "METHOD": MistralMethods.CHAT_STREAM.value,
        "ENDPOINT": "/v1/chat/completions",
    },
    "EMBEDDINGS_CREATE": {
        "METHOD": MistralMethods.EMBEDDINGS_CREATE.value,
        "ENDPOINT": "/v1/embeddings",
    },
    "ASYNC_EMBEDDINGS_CREATE": {
        "METHOD": MistralMethods.ASYNC_EMBEDDINGS_CREATE.value,
        "ENDPOINT": "/v1/embeddings",
    },
}
