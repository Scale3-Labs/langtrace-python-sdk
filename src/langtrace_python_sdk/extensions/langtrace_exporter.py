import json
import os
import typing

import requests
from opentelemetry.sdk.trace.export import ReadableSpan, SpanExporter, SpanExportResult
from opentelemetry.trace.span import format_trace_id

from langtrace_python_sdk.constants.exporter.langtrace_exporter import (
    LANGTRACE_REMOTE_URL,
)


class LangTraceExporter(SpanExporter):
    """
    **LangTraceExporter Class**

    This class exports telemetry data in the LangTrace format to a remote URL. It inherits from the `SpanExporter` class in OpenTelemetry.

    **Purpose:**

    - Provides a mechanism to export trace data from your application to a LangTrace collector.
    - Offers a convenient way to send spans with their attributes, events, and links.

    **Attributes:**

    * `api_key` (str): An API key to authenticate with the LangTrace collector (required).
    * `write_to_remote_url` (bool): A flag indicating whether to send spans to the remote URL (defaults to False).

    **Methods:**

    * `__init__(api_key: str = None, url: str = None, write_to_remote_url: bool = False) -> None`:
        - Initializes a `LangTraceExporter` instance.
        - Retrieves the API key and URL from environment variables if not provided explicitly.
        - Raises a `ValueError` if the API key is missing or the URL is missing when `write_to_remote_url` is True.
    * `export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult`:
        - Exports a batch of `opentelemetry.trace.Span` objects to LangTrace.
        - Converts each span into a dictionary representation including trace ID, instrumentation library, events, dropped data counts, duration, and other span attributes.
        - If `write_to_remote_url` is False, returns `SpanExportResult.SUCCESS` without sending data.
        - Otherwise, sends the data to the configured URL using a POST request with JSON data and the API key in the header.
        - Returns `SpanExportResult.SUCCESS` on successful export or `SpanExportResult.FAILURE` on errors.
    * `shutdown(self) -> None`:
        - (Optional) Performs any necessary cleanup tasks when the exporter is shut down. Currently does nothing.

    **Raises:**

    * `ValueError`: If the API key is not provided or the URL is missing when `write_to_remote_url` is True.
    """

    api_key: str
    write_to_remote_url: bool

    def __init__(
        self,
        api_key: str = None,
        write_to_remote_url: bool = False,
        api_host: typing.Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("LANGTRACE_API_KEY")
        self.write_to_remote_url = write_to_remote_url
        self.api_host: str = api_host or LANGTRACE_REMOTE_URL

        if self.write_to_remote_url and not self.api_key:
            raise ValueError("No API key provided")

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Exports a batch of telemetry data.

        Args:
            spans: The list of `opentelemetry.trace.Span` objects to be exported

        Returns:
            The result of the export SUCCESS or FAILURE
        """
        data = [
            {
                "traceId": format_trace_id(span.get_span_context().trace_id),
                "instrumentationLibrary": span.instrumentation_info.__repr__(),
                "droppedEventsCount": span.dropped_events,
                "droppedAttributesCount": span.dropped_attributes,
                "droppedLinksCount": span.dropped_links,
                "ended": span.status.is_ok,
                **json.loads(span.to_json()),
            }
            for span in spans
        ]

        if not self.write_to_remote_url:
            return

        # Send data to remote URL
        try:
            requests.post(
                url=f"{self.api_host}/api/trace",
                data=json.dumps(data),
                headers={"Content-Type": "application/json", "x-api-key": self.api_key},
            )
            print(f"sent to {self.api_host}/api/trace with {len(data)} spans")
            return SpanExportResult.SUCCESS
        except Exception as e:
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        pass
