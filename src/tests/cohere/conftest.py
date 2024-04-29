"""Unit tests configuration module."""

import pytest
import os
import cohere

from langtrace_python_sdk.instrumentation.cohere.instrumentation import (
    CohereInstrumentation,
)


@pytest.fixture(autouse=True)
def environment():
    if not os.getenv("CO_API_KEY"):
        os.environ["CO_API_KEY"] = "test_co_api_key"


@pytest.fixture
def cohere_client():
    return cohere.Client(os.environ["CO_API_KEY"])


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.fixture(scope="session", autouse=True)
def instrument():
    CohereInstrumentation().instrument()
