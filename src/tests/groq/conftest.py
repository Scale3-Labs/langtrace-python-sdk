import os
import pytest

from groq import Groq, AsyncGroq
from langtrace_python_sdk.instrumentation import GroqInstrumentation
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(autouse=True)
def environment():
    os.environ["GROQ_API_KEY"] = "test_api_key"


@pytest.fixture
def groq_client():
    return Groq()


@pytest.fixture
def async_groq_client():
    return AsyncGroq()


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization", "api-key"]}


@pytest.fixture(scope="session", autouse=True)
def instrument():
    GroqInstrumentation().instrument()
