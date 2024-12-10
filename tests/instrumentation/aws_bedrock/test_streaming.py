"""Tests for AWS Bedrock streaming support."""
import pytest
from unittest.mock import Mock, patch

from langtrace_python_sdk.instrumentation.aws_bedrock.streaming import StreamWrapper


def test_stream_wrapper_basic():
    """Test basic streaming functionality."""
    mock_stream = iter(["chunk1", "chunk2", "chunk3"])
    wrapper = StreamWrapper(mock_stream)

    chunks = list(wrapper)
    assert chunks == ["chunk1", "chunk2", "chunk3"]
    assert wrapper.get_buffer() == chunks


def test_stream_wrapper_callback():
    """Test streaming with callback."""
    mock_stream = iter(["chunk1", "chunk2", "chunk3"])
    mock_callback = Mock()
    wrapper = StreamWrapper(mock_stream, callback=mock_callback)

    list(wrapper)  # Consume the stream
    mock_callback.assert_called_once_with(["chunk1", "chunk2", "chunk3"])


def test_stream_wrapper_empty():
    """Test streaming with empty stream."""
    mock_stream = iter([])
    mock_callback = Mock()
    wrapper = StreamWrapper(mock_stream, callback=mock_callback)

    chunks = list(wrapper)
    assert chunks == []
    assert wrapper.get_buffer() == []
    mock_callback.assert_not_called()


def test_stream_wrapper_error():
    """Test streaming with error in stream."""
    def error_stream():
        yield "chunk1"
        raise ValueError("Stream error")
        yield "chunk2"  # This won't be reached

    mock_callback = Mock()
    wrapper = StreamWrapper(error_stream(), callback=mock_callback)

    with pytest.raises(ValueError, match="Stream error"):
        list(wrapper)

    assert wrapper.get_buffer() == ["chunk1"]
    mock_callback.assert_called_once_with(["chunk1"])


def test_stream_wrapper_callback_error():
    """Test streaming with error in callback."""
    mock_stream = iter(["chunk1", "chunk2"])
    mock_callback = Mock(side_effect=ValueError("Callback error"))
    wrapper = StreamWrapper(mock_stream, callback=mock_callback)

    with pytest.raises(ValueError, match="Callback error"):
        list(wrapper)

    assert wrapper.get_buffer() == ["chunk1", "chunk2"]
    mock_callback.assert_called_once_with(["chunk1", "chunk2"])
