"""Unit tests configuration module."""

import pytest
import os
from anthropic import Anthropic, AsyncAnthropic

from langtrace_python_sdk.instrumentation.anthropic.instrumentation import (
    AnthropicInstrumentation,
)


@pytest.fixture(autouse=True)
def environment():
    if not os.getenv("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = "test_api_key"


@pytest.fixture
def anthropic_client():
    return Anthropic()


@pytest.fixture
def async_anthropic_client():
    return AsyncAnthropic()


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization", "x-api-key"]}


@pytest.fixture(scope="session", autouse=True)
def instrument():
    AnthropicInstrumentation().instrument()
