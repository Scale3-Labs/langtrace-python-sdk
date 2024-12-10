import os
import json
import pytest
from typing import Dict, Iterator
from unittest.mock import patch, MagicMock

from langtrace_python_sdk import langtrace
from examples.awsbedrock_examples.converse import use_converse, use_converse_stream

@pytest.fixture
def mock_env():
    """Provide mock environment variables for testing."""
    with patch.dict(os.environ, {
        "LANGTRACE_API_KEY": "test_key",
        "AWS_ACCESS_KEY_ID": "test_aws_key",
        "AWS_SECRET_ACCESS_KEY": "test_aws_secret"
    }):
        yield

@pytest.fixture
def mock_bedrock_client():
    """Provide a mocked AWS Bedrock client."""
    with patch("boto3.client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.invoke_model.side_effect = mock_invoke_model
        mock_instance.invoke_model_with_response_stream.side_effect = mock_invoke_model_with_response_stream
        yield mock_instance

def mock_invoke_model(*args, **kwargs) -> Dict:
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
        "output": {
            "message": {
                "content": [{"text": "Mocked response for testing with vendor attributes"}]
            }
        }
    }
    return {
        'body': json.dumps(mock_response).encode()
    }

def mock_invoke_model_with_response_stream(*args, **kwargs) -> Dict:
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
                    "output": {
                        "message": {
                            "content": [{"text": "Streaming chunk 1"}]
                        }
                    }
                }).encode()
            }
        },
        {
            'chunk': {
                'bytes': json.dumps({
                    "output": {
                        "message": {
                            "content": [{"text": "Streaming chunk 2"}]
                        }
                    }
                }).encode()
            }
        }
    ]
    return {'body': chunks}

@pytest.mark.usefixtures("mock_env")
class TestAWSBedrock:
    """Test suite for AWS Bedrock instrumentation."""

    def test_standard_completion(self, mock_bedrock_client):
        """Test standard completion with mocked AWS client."""
        response = use_converse("Tell me about OpenTelemetry")
        assert response is not None
        content = response.get('output', {}).get('message', {}).get('content', [])
        assert content, "Response content should not be empty"
        assert isinstance(content[0].get('text'), str), "Response text should be a string"

    def test_streaming_completion(self, mock_bedrock_client):
        """Test streaming completion with mocked AWS client."""
        chunks = list(use_converse_stream("What is distributed tracing?"))
        assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"

        for chunk in chunks:
            content = chunk.get('output', {}).get('message', {}).get('content', [])
            assert content, "Chunk content should not be empty"
            assert isinstance(content[0].get('text'), str), "Chunk text should be a string"
