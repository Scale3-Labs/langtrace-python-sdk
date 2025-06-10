from langtrace.trace_attributes import AWSBedrockMethods

APIS = {
    "INVOKE_MODEL": {
        "METHOD": "aws_bedrock.invoke_model",
        "ENDPOINT": "/invoke-model",
    },
    "INVOKE_MODEL_WITH_RESPONSE_STREAM": {
        "METHOD": "aws_bedrock.invoke_model_with_response_stream",
        "ENDPOINT": "/invoke-model-with-response-stream",
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
