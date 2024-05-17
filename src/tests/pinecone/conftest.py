import pytest
import os
from langtrace_python_sdk.instrumentation.pinecone.instrumentation import (
    PineconeInstrumentation,
)
from langtrace_python_sdk.instrumentation.openai.instrumentation import (
    OpenAIInstrumentation,
)
from openai import OpenAI
from pinecone import Pinecone


@pytest.fixture(autouse=True)
def environment():
    if not os.getenv("PINECONE_API_KEY"):
        os.environ["PINECONE_API_KEY"] = "test_pinecone_api_key"
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test_api_key"


@pytest.fixture
def pinecone_client():
    return Pinecone()


@pytest.fixture
def openai_client():
    return OpenAI()


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.fixture(autouse=True, scope="session")
def instrument():
    OpenAIInstrumentation().instrument()
    PineconeInstrumentation().instrument()
