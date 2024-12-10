"""Streaming support for AWS Bedrock instrumentation."""
from typing import Any, Callable, Iterator, List, Optional, TypeVar
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)

class StreamWrapper:
    """Wrapper for AWS Bedrock streaming responses.

    Buffers streaming responses and provides callback functionality
    while maintaining the original stream's behavior.

    Args:
        stream: The original stream to wrap
        callback: Optional callback to call with buffered content when stream ends

    Example:
        >>> def on_complete(buffer):
        ...     print(f"Stream complete with {len(buffer)} chunks")
        >>> stream = StreamWrapper(original_stream, callback=on_complete)
        >>> for chunk in stream:
        ...     process_chunk(chunk)
    """

    def __init__(self, stream: Iterator[T], callback: Optional[Callable[[List[T]], None]] = None):
        """Initialize the stream wrapper."""
        if not hasattr(stream, '__iter__'):
            raise ValueError("Stream must be iterable")
        self._stream = stream
        self._callback = callback
        self._buffer: List[T] = []

    def __iter__(self) -> Iterator[T]:
        """Iterate over the stream, buffering content and yielding chunks."""
        try:
            for chunk in self._stream:
                try:
                    self._buffer.append(chunk)
                    yield chunk
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    raise
        except Exception as e:
            logger.error(f"Error in stream: {e}")
            raise
        finally:
            if self._callback and self._buffer:
                try:
                    self._callback(self._buffer)
                except Exception as e:
                    logger.error(f"Error in stream callback: {e}")
                    raise

    def get_buffer(self) -> List[T]:
        """Get the current buffer contents.

        Returns:
            List of buffered chunks
        """
        return self._buffer.copy()
