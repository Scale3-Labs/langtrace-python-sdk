"""Configuration options for AWS Bedrock instrumentation."""
import os
from typing import Optional


class BedrockConfig:
    """Configuration for AWS Bedrock instrumentation.

    Controls tracing behavior and vendor-specific settings through environment variables.
    All settings are opt-in and maintain backward compatibility.
    """

    @property
    def trace_content(self) -> bool:
        """Control whether to trace prompt and completion content.

        Returns:
            bool: True if content should be traced, False otherwise.
            Defaults to True for backward compatibility.
        """
        return os.getenv("LANGTRACE_TRACE_CONTENT", "true").lower() == "true"

    @property
    def vendor_specific_attributes(self) -> bool:
        """Control whether to include vendor-specific attributes in spans.

        Returns:
            bool: True if vendor-specific attributes should be included, False otherwise.
            Defaults to True for backward compatibility.
        """
        return os.getenv("LANGTRACE_VENDOR_ATTRIBUTES", "true").lower() == "true"

    @property
    def stream_buffer_enabled(self) -> bool:
        """Control whether to buffer streaming responses.

        Returns:
            bool: True if streaming responses should be buffered, False otherwise.
            Defaults to True for better tracing capabilities.
        """
        return os.getenv("LANGTRACE_STREAM_BUFFER", "true").lower() == "true"
