import json
import os
import typing
import sys

import requests
from opentelemetry.sdk.trace.export import ReadableSpan, SpanExporter, SpanExportResult
from opentelemetry.trace.span import format_trace_id

from langtrace_python_sdk.constants.exporter.langtrace_exporter import (
    LANGTRACE_REMOTE_URL,
)
from colorama import Fore
from requests.exceptions import RequestException


class LangTraceExporter(SpanExporter):
    """
    **LangTraceExporter Class**

    This class exports telemetry data in the LangTrace format to a remote URL. It inherits from the `SpanExporter` class in OpenTelemetry.

    **Purpose:**

    - Provides a mechanism to export trace data from your application to a LangTrace collector.
    - Offers a convenient way to send spans with their attributes, events, and links.

    **Attributes:**

    * `api_key` (str): An API key to authenticate with the LangTrace collector (required).

    **Methods:**

    * `__init__(api_key: str = None, url: str = None) -> None`:
        - Initializes a `LangTraceExporter` instance.
        - Retrieves the API key and URL from environment variables if not provided explicitly.
        - Raises a `ValueError` if the API key is missing.
    * `export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult`:
        - Exports a batch of `opentelemetry.trace.Span` objects to LangTrace.
        - Converts each span into a dictionary representation including trace ID, instrumentation library, events, dropped data counts, duration, and other span attributes.
        - Otherwise, sends the data to the configured URL using a POST request with JSON data and the API key in the header.
        - Returns `SpanExportResult.SUCCESS` on successful export or `SpanExportResult.FAILURE` on errors.
    * `shutdown(self) -> None`:
        - (Optional) Performs any necessary cleanup tasks when the exporter is shut down. Currently does nothing.

    **Raises:**

    * `ValueError`: If the API key is not provided.
    """

    api_key: str
    api_host: str
    disable_logging: bool

    def __init__(
        self,
        api_host,
        api_key: str = None,
        disable_logging: bool = False,
    ) -> None:
        self.api_key = api_key or os.environ.get("LANGTRACE_API_KEY")
        self.api_host = (
            f"{LANGTRACE_REMOTE_URL}/api/trace"
            if api_host == LANGTRACE_REMOTE_URL
            else api_host
        )
        self.disable_logging = disable_logging

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Exports a batch of telemetry data.

        Args:
            spans: The list of `opentelemetry.trace.Span` objects to be exported

        Returns:
            The result of the export SUCCESS or FAILURE
        """
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "User-Agent": "LangtraceExporter",
        }

        # Check if the OTEL_EXPORTER_OTLP_HEADERS environment variable is set
        otel_headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", None)
        if otel_headers:
            # Parse and add to headers
            for header in otel_headers.split(","):
                key, value = header.split("=")
                headers[key.strip()] = value.strip()

        # Check if the OTEL_EXPORTER_OTLP_TRACES_HEADERS environment variable is set
        otel_traces_headers = os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS", None)
        if otel_traces_headers:
            # Parse and add to headers
            for header in otel_traces_headers.split(","):
                key, value = header.split("=")
                headers[key.strip()] = value.strip()

        if not headers["x-api-key"] and not self.disable_logging:
            print(Fore.RED)
            print(
                "Missing Langtrace API key, proceed to https://langtrace.ai to create one"
            )
            print("Set the API key as an environment variable LANGTRACE_API_KEY")
            print(Fore.RESET)
            return
        data = [
            {
                "traceId": format_trace_id(span.get_span_context().trace_id),
                "droppedEventsCount": span.dropped_events,
                "droppedAttributesCount": span.dropped_attributes,
                "droppedLinksCount": span.dropped_links,
                "ended": span.status.is_ok,
                **json.loads(span.to_json()),
            }
            for span in spans
        ]

        # Send data to remote URL
        try:
            response = requests.post(
                url=f"{self.api_host}",
                data=json.dumps(data),
                headers=headers,
                timeout=40,
            )

            if not response.ok:
                raise RequestException(response.text)
            if not self.disable_logging:
                print(
                    Fore.GREEN
                    + f"Exported {len(spans)} spans successfully."
                    + Fore.RESET
                )
            return SpanExportResult.SUCCESS
        except RequestException as err:
            if not self.disable_logging:
                print(Fore.RED + "Failed to export spans.")
                print(Fore.RED + f"Error: {err}\r\n" + Fore.RESET)
                if (
                    "invalid api key" in str(err).lower()
                    and self.api_host == f"{LANGTRACE_REMOTE_URL}/api/trace"
                ):
                    print(
                        Fore.YELLOW
                        + "If you're self-hosting Langtrace, make sure to do one of the following to configure your trace endpoint (e.g., http://localhost:3000/api/trace):"
                        + Fore.YELLOW
                    )
                    print(
                        Fore.YELLOW
                        + "1. Set the `LANGTRACE_API_HOST` environment variable, or\r\n2. Pass the `api_host` parameter to the `langtrace.init()` method.\r\n"
                        + Fore.YELLOW
                    )
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        print(
            Fore.WHITE
            + "⭐ Leave our github a star to stay on top of our updates - https://github.com/Scale3-Labs/langtrace"
            + Fore.RESET
        )
