"""Unit tests configuration module."""

import os
import pytest

from langtrace_python_sdk.instrumentation.openai.instrumentation import (
    OpenAIInstrumentation,
)
from langtrace_python_sdk.instrumentation.langchain.instrumentation import (
    LangchainInstrumentation,
)
from langtrace_python_sdk.instrumentation.langchain_core.instrumentation import (
    LangchainCoreInstrumentation,
)

from langtrace_python_sdk.instrumentation.langchain_community.instrumentation import (
    LangchainCommunityInstrumentation,
)


@pytest.fixture(autouse=True)
def clear_exporter(exporter):
    exporter.clear()


@pytest.fixture(autouse=True)
def environment():
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test"


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization", "x-api-key"]}


@pytest.fixture(scope="session", autouse=True)
def instrument():
    OpenAIInstrumentation().instrument()
    LangchainInstrumentation().instrument()
    LangchainCoreInstrumentation().instrument()
    LangchainCommunityInstrumentation().instrument()
