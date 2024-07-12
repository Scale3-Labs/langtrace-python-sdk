from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.groq import APIS
import pytest
from langtrace.trace_attributes import SpanAttributes
from importlib_metadata import version as v
from tests.utils import (
    assert_completion_in_events,
    assert_prompt_in_events,
    assert_response_format,
    assert_token_count,
)


@pytest.mark.vcr
def test_chat_completion(exporter, groq_client):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        model="llama3-8b-8192",
    )

    spans = exporter.get_finished_spans()
    groq_span = spans[-1]

    assert groq_span.name == "groq.chat.completions.create"
    attributes = groq_span.attributes
    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "Groq"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("groq")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.groq.com"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )
    assert_token_count(attributes)
    assert_prompt_in_events(groq_span.events)
    assert_completion_in_events(groq_span.events)


@pytest.mark.vcr()
@pytest.mark.asyncio()
async def test_async_chat_completion(exporter, async_groq_client):
    chat_completion = await async_groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        model="llama3-8b-8192",
    )
    spans = exporter.get_finished_spans()
    groq_span = spans[-1]

    assert groq_span.name == "groq.chat.completions.create"
    attributes = groq_span.attributes
    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "Groq"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("groq")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.groq.com"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )
    assert_token_count(attributes)
    assert_prompt_in_events(groq_span.events)
    assert_completion_in_events(groq_span.events)


@pytest.mark.vcr()
def test_chat_completion_streaming(exporter, groq_client):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        stream=True,
        model="llama3-8b-8192",
    )

    for _ in chat_completion:
        pass

    spans = exporter.get_finished_spans()
    groq_span = spans[-1]
    assert groq_span.name == "groq.chat.completions.create"
    attributes = groq_span.attributes
    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "Groq"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("groq")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.groq.com"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )

    assert_token_count(attributes)
    assert_completion_in_events(groq_span.events)


@pytest.mark.vcr()
@pytest.mark.asyncio()
async def test_async_chat_completion_streaming(async_groq_client, exporter):
    chat_completion = await async_groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        stream=True,
        model="llama3-8b-8192",
    )

    async for _ in chat_completion:
        pass

    spans = exporter.get_finished_spans()
    groq_span = spans[-1]
    assert groq_span.name == "groq.chat.completions.create"
    attributes = groq_span.attributes
    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "Groq"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("groq")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.groq.com"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )

    assert_token_count(attributes)
    assert_completion_in_events(groq_span.events)
