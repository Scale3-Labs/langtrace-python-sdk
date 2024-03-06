"""
APIs to instrument OpenAI.
"""
from langtrace.trace_attributes import OpenAIMethods

APIS = {
    "CHAT_COMPLETION": {
        "METHOD": OpenAIMethods.CHAT_COMPLETION.value,
        "ENDPOINT": "/chat/completions",
    },
    "IMAGES_GENERATION": {
        "METHOD": OpenAIMethods.IMAGES_GENERATION.value,
        "ENDPOINT": "/images/generations",
    },
    "EMBEDDINGS_CREATE": {
        "METHOD": OpenAIMethods.EMBEDDINGS_CREATE.value,
        "ENDPOINT": "/embeddings",
    },
}
