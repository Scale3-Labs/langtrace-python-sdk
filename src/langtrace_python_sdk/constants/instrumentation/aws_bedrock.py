from langtrace.trace_attributes import AWSBedrockMethods

APIS = {
    "INVOKE_MODEL": {
        "METHOD": "aws_bedrock.invoke_model",
        "ENDPOINT": "/invoke-model",
    },
    "CONVERSE": {
        "METHOD": AWSBedrockMethods.CONVERSE.value,
        "ENDPOINT": "/converse",
    },
    "CONVERSE_STREAM": {
        "METHOD": AWSBedrockMethods.CONVERSE_STREAM.value,
        "ENDPOINT": "/converse-stream",
    },
}
