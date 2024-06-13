"""Unit tests configuration module."""

import pytest
import os
from openai import OpenAI, AsyncOpenAI
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


@pytest.fixture(scope="session", autouse=True)
def instrument():
    OpenAIInstrumentation().instrument()
