import os
import boto3
from typing import Dict, Iterator

from opentelemetry import trace
from opentelemetry.trace import TracerProvider
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from langtrace_python_sdk.instrumentation.aws_bedrock import AWSBedrockInstrumentation

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
AWSBedrockInstrumentation().instrument()
langtrace.init()

def get_bedrock_client():
    """Create an instrumented AWS Bedrock client."""
    return boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

@with_langtrace_root_span()
def use_converse() -> Dict:
    """Example of standard completion request with vendor attributes."""
    client = get_bedrock_client()
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    try:
        response = client.converse(
            modelId=model_id,
            messages=[{
                "role": "user",
                "content": [{"text": "Write a story about a magic backpack."}],
            }],
            inferenceConfig={
                "maxTokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "stopSequences": ["\n\nHuman:"],
            },
            additionalModelRequestFields={
                "top_k": 250,
                "anthropic_version": "bedrock-2024-02-20",
            }
        )
        return response
    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        raise

@with_langtrace_root_span()
def use_converse_stream() -> Iterator[Dict]:
    """Example of streaming completion with vendor attributes."""
    client = get_bedrock_client()
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    try:
        response = client.converse_stream(
            modelId=model_id,
            messages=[{
                "role": "user",
                "content": [{"text": "Tell me a story about a robot learning to dance."}],
            }],
            inferenceConfig={
                "maxTokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "stopSequences": ["\n\nHuman:"],
            },
            additionalModelRequestFields={
                "top_k": 250,
                "anthropic_version": "bedrock-2024-02-20",
            }
        )
        return response
    except Exception as e:
        print(f"ERROR: Can't invoke streaming for '{model_id}'. Reason: {e}")
        raise
