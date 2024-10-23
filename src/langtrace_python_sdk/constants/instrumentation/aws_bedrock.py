from langtrace.trace_attributes import AWSBedrockMethods

APIS = {
    "CONVERSE": {
        "METHOD": AWSBedrockMethods.CONVERSE.value,
        "ENDPOINT": "/converse",
    },
    "CONVERSE_STREAM": {
        "METHOD": AWSBedrockMethods.CONVERSE_STREAM.value,
        "ENDPOINT": "/converse-stream",
    },
}
