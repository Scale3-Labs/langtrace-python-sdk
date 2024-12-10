import os
import json
import boto3
from unittest.mock import patch
from langtrace_python_sdk import langtrace
from examples.awsbedrock_examples.converse import use_converse, use_converse_stream

def mock_invoke_model(*args, **kwargs):
    """Mock for standard completion with vendor attribute verification."""
    # Verify the request body contains all expected attributes
    body = json.loads(kwargs.get('body', '{}'))

    assert body.get('max_tokens') == 4096, f"Incorrect max_tokens: {body.get('max_tokens')}"
    assert body.get('temperature') == 0.7, f"Incorrect temperature: {body.get('temperature')}"
    assert body.get('top_p') == 0.9, f"Incorrect top_p: {body.get('top_p')}"
    assert body.get('top_k') == 250, f"Incorrect top_k: {body.get('top_k')}"
    assert body.get('stop_sequences') == ["\n\nHuman:"], f"Incorrect stop_sequences: {body.get('stop_sequences')}"
    assert body.get('anthropic_version') == "bedrock-2024-02-20", f"Incorrect anthropic_version: {body.get('anthropic_version')}"
    assert kwargs.get('modelId') == "anthropic.claude-3-haiku-20240307-v1:0", f"Incorrect modelId: {kwargs.get('modelId')}"

    mock_response = {
        "completion": "Mocked response for testing with vendor attributes",
        "stop_reason": "stop_sequence",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30
        }
    }
    return {
        'body': json.dumps(mock_response).encode()
    }

def mock_invoke_model_with_response_stream(*args, **kwargs):
    """Mock for streaming completion with vendor attribute verification."""
    # Verify the request body contains all expected attributes
    body = json.loads(kwargs.get('body', '{}'))

    assert body.get('max_tokens') == 4096, f"Incorrect max_tokens: {body.get('max_tokens')}"
    assert body.get('temperature') == 0.7, f"Incorrect temperature: {body.get('temperature')}"
    assert body.get('top_p') == 0.9, f"Incorrect top_p: {body.get('top_p')}"
    assert body.get('top_k') == 250, f"Incorrect top_k: {body.get('top_k')}"
    assert body.get('stop_sequences') == ["\n\nHuman:"], f"Incorrect stop_sequences: {body.get('stop_sequences')}"
    assert body.get('anthropic_version') == "bedrock-2024-02-20", f"Incorrect anthropic_version: {body.get('anthropic_version')}"
    assert kwargs.get('modelId') == "anthropic.claude-3-haiku-20240307-v1:0", f"Incorrect modelId: {kwargs.get('modelId')}"

    chunks = [
        {
            'chunk': {
                'bytes': json.dumps({
                    "completion": "Streaming chunk 1",
                    "stop_reason": None
                }).encode()
            }
        },
        {
            'chunk': {
                'bytes': json.dumps({
                    "completion": "Streaming chunk 2",
                    "stop_reason": "stop_sequence"
                }).encode()
            }
        }
    ]
    return {'body': chunks}

def run_test():
    """Run tests for both standard and streaming completion."""
    # Initialize Langtrace with API key from environment
    langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

    with patch("boto3.client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.invoke_model = mock_invoke_model
        mock_instance.invoke_model_with_response_stream = mock_invoke_model_with_response_stream

        print("\nTesting AWS Bedrock instrumentation...")

        try:
            # Test standard completion
            print("\nTesting standard completion...")
            response = use_converse("Tell me about OpenTelemetry")
            print(f"Standard completion response: {response}")
            print("✓ Standard completion test passed with vendor attributes")

            # Test streaming completion
            print("\nTesting streaming completion...")
            chunks = []
            for chunk in use_converse_stream("What is distributed tracing?"):
                chunks.append(chunk)
                print(f"Streaming chunk: {chunk}")
            assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
            print(f"✓ Streaming completion test passed with {len(chunks)} chunks")

            print("\n✓ All tests completed successfully!")
        except AssertionError as e:
            print(f"\n❌ Test failed: {str(e)}")
            raise


if __name__ == "__main__":
    run_test()
