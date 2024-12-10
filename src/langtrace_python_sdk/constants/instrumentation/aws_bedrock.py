from enum import Enum
from langtrace.trace_attributes import AWSBedrockMethods, SpanAttributes

class AWSBedrockAttributes(str, Enum):
    MODEL_ID = "aws.bedrock.model.id"
    TEMPERATURE = "aws.bedrock.temperature"
    TOP_P = "aws.bedrock.top_p"
    TOP_K = "aws.bedrock.top_k"
    MAX_TOKENS = "aws.bedrock.max_tokens"
    STOP_SEQUENCES = "aws.bedrock.stop_sequences"
    RESPONSE_FILTER = "aws.bedrock.response_filter"
    ANTHROPIC_VERSION = "aws.bedrock.anthropic.version"
    COHERE_TRUNCATE = "aws.bedrock.cohere.truncate"
    AI21_PENALTY = "aws.bedrock.ai21.penalty"

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

MODEL_PROVIDERS = {
    "anthropic.claude": "anthropic",
    "cohere.command": "cohere",
    "ai21.j2": "ai21",
    "amazon.titan": "amazon",
    "meta.llama2": "meta",
}
