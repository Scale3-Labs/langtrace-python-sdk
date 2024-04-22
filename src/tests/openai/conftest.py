"""Unit tests configuration module."""

import pytest
import os
from openai import OpenAI, AsyncOpenAI
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace
from langtrace_python_sdk.instrumentation.openai.instrumentation import (
    OpenAIInstrumentation,
)


@pytest.fixture(autouse=True)
def environment():
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test_api_key"


@pytest.fixture
def openai_client():
    return OpenAI()


@pytest.fixture
def async_openai_client():
    return AsyncOpenAI()


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization", "api-key"]}


@pytest.fixture(scope="session")
def exporter():
    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)

    provider = TracerProvider()
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    OpenAIInstrumentation().instrument()
    return exporter
