import chromadb
import pytest
from langtrace_python_sdk.instrumentation.chroma.instrumentation import (
    ChromaInstrumentation,
)


@pytest.fixture
def chroma_client():
    return chromadb.Client()


@pytest.fixture(scope="session", autouse=True)
def instrument():
    ChromaInstrumentation().instrument()
