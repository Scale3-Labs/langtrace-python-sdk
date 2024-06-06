from langtrace.trace_attributes import OpenAIMethods

OPENAI_COST_TABLE = {
    "gpt-4-0125-preview": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-4-1106-preview": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-4-1106-vision-preview": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-4": {
        "input": 0.03,
        "output": 0.06,
    },
    "gpt-4-32k": {
        "input": 0.06,
        "output": 0.12,
    },
    "gpt-3.5-turbo-0125": {
        "input": 0.0005,
        "output": 0.0015,
    },
    "gpt-3.5-turbo-instruct": {
        "input": 0.0015,
        "output": 0.002,
    },
}

APIS = {
    "CHAT_COMPLETION": {
        "METHOD": OpenAIMethods.CHAT_COMPLETION.value,
        "ENDPOINT": "/chat/completions",
    },
    "IMAGES_GENERATION": {
        "METHOD": OpenAIMethods.IMAGES_GENERATION.value,
        "ENDPOINT": "/images/generations",
    },
    "IMAGES_EDIT": {
        "METHOD": OpenAIMethods.IMAGES_EDIT.value,
        "ENDPOINT": "/images/edits",
    },
    "EMBEDDINGS_CREATE": {
        "METHOD": OpenAIMethods.EMBEDDINGS_CREATE.value,
        "ENDPOINT": "/embeddings",
    },
}
