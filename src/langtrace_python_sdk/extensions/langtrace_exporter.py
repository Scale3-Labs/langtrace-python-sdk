import json
import os
import typing

import requests
from opentelemetry.sdk.trace.export import (ReadableSpan, SpanExporter,
                                            SpanExportResult)

from opentelemetry.trace.span import format_trace_id
class LangTraceExporter(SpanExporter):
    api_key: str
    url: str
    write_to_remote_url: bool

    def __init__(self, api_key: str = None, url: str = None, write_to_remote_url: bool = False) -> None:
        self.api_key = api_key if api_key else os.environ.get(
            'LANGTRACE_API_KEY')
        self.url = url if url else os.environ.get('LANGTRACE_URL')
        self.write_to_remote_url = write_to_remote_url

        if not self.api_key:
            raise ValueError('No API key provided')

        if not self.url and self.write_to_remote_url:
            raise ValueError('No URL provided')

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
                'traceId': format_trace_id(span.get_span_context().trace_id),
                'instrumentationLibrary': span.instrumentation_info.__repr__(),
                'droppedEventsCount': span.dropped_events,
                'droppedAttributesCount': span.dropped_attributes,
                'droppedLinksCount': span.dropped_links,
                'ended': span.status.is_ok,
                'duration': span.end_time - span.start_time,
                **json.loads(span.to_json()),
            } for span in spans]

        if not self.write_to_remote_url:
            return

        # Send data to remote URL
        try:
            requests.post(
                url=self.url,
                data=json.dumps(data),
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key
                }
            )
            print(f"Sent To {self.url} with Body {data} ")
            return SpanExportResult.SUCCESS
        except Exception as e:
            print("Error sending data to remote URL", e)
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        pass
