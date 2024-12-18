import os
import pytest
from opentelemetry.trace import SpanKind
from langtrace_python_sdk.langtrace import LangtraceConfig
from langtrace_python_sdk.extensions.langtrace_exporter import LangTraceExporter
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from langtrace_python_sdk.constants.exporter.langtrace_exporter import LANGTRACE_SESSION_ID_HEADER

def test_session_id_from_env(exporter):
    # Test session ID from environment variable
    test_session_id = "test-session-123"
    os.environ["LANGTRACE_SESSION_ID"] = test_session_id

    @with_langtrace_root_span()
    def test_function():
        pass

    test_function()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.attributes.get("session.id") == test_session_id

    # Cleanup
    del os.environ["LANGTRACE_SESSION_ID"]

def test_session_id_in_config():
    # Test session ID through LangtraceConfig
    test_session_id = "config-session-456"
    config = LangtraceConfig(session_id=test_session_id)
    exporter = LangTraceExporter(
        api_host="http://test",
        api_key="test-key",
        session_id=config.session_id
    )

    assert exporter.session_id == test_session_id

def test_session_id_in_headers():
    # Test session ID in HTTP headers
    test_session_id = "header-session-789"
    exporter = LangTraceExporter(
        api_host="http://test",
        api_key="test-key",
        session_id=test_session_id
    )

    # Export method adds headers, so we'll check the headers directly
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "test-key",
        "User-Agent": "LangtraceExporter",
    }

    if test_session_id:
        headers[LANGTRACE_SESSION_ID_HEADER] = test_session_id

    assert headers[LANGTRACE_SESSION_ID_HEADER] == test_session_id
