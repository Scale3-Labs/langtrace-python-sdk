import chromadb
import pytest
from langtrace_python_sdk.instrumentation.chroma.instrumentation import (
    ChromaInstrumentation,
)

from os import getcwd


@pytest.fixture
def chroma_client():
    return chromadb.PersistentClient(getcwd())


@pytest.fixture(scope="session", autouse=True)
def instrument():
    ChromaInstrumentation().instrument()
