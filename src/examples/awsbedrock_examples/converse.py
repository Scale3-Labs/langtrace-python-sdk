import os
import json
import boto3
from typing import Dict, Iterator

from opentelemetry import trace
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.instrumentation.aws_bedrock import AWSBedrockInstrumentation

# Initialize instrumentation
AWSBedrockInstrumentation().instrument()
langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

def get_bedrock_client():
    """Create an instrumented AWS Bedrock client."""
    return boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

@trace.get_tracer(__name__).start_as_current_span("bedrock_converse")
def use_converse(input_text: str) -> Dict:
    """Example of standard completion request with vendor attributes."""
    client = get_bedrock_client()
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "messages": [{
                    "role": "user",
                    "content": [{"text": input_text}],
                }],
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 250,
                "stop_sequences": ["\n\nHuman:"],
                "anthropic_version": "bedrock-2024-02-20"
            })
        )
        # Handle both StreamingBody and bytes response types
        body = response['body']
        if hasattr(body, 'read'):
            content = body.read()
        else:
            content = body
        return json.loads(content)
    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        raise

@trace.get_tracer(__name__).start_as_current_span("bedrock_converse_stream")
def use_converse_stream(input_text: str) -> Iterator[Dict]:
    """Example of streaming completion with vendor attributes."""
    client = get_bedrock_client()
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    try:
        response = client.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps({
                "messages": [{
                    "role": "user",
                    "content": [{"text": input_text}],
                }],
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 250,
                "stop_sequences": ["\n\nHuman:"],
                "anthropic_version": "bedrock-2024-02-20"
            })
        )
        for event in response.get('body'):
            if 'chunk' in event:
                chunk_bytes = event['chunk']['bytes']
                if isinstance(chunk_bytes, (str, bytes)):
                    yield json.loads(chunk_bytes)
                else:
                    yield json.loads(chunk_bytes.read())
    except Exception as e:
        print(f"ERROR: Can't invoke streaming for '{model_id}'. Reason: {e}")
        raise
