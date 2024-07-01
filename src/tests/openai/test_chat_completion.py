import pytest
import json
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from tests.utils import assert_response_format, assert_token_count
from importlib_metadata import version as v
from langtrace.trace_attributes import SpanAttributes


@pytest.mark.vcr()
def test_chat_completion(exporter, openai_client):
    llm_model_value = "gpt-4"
    messages_value = [{"role": "user", "content": "Say this is a test three times"}]

    kwargs = {
        "model": llm_model_value,
        "messages": messages_value,
        "stream": False,
    }

    openai_client.chat.completions.create(**kwargs)
    spans = exporter.get_finished_spans()
    completion_span = spans[-1]
    assert completion_span.name == "openai.chat.completions.create"

    attributes = completion_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == "langtrace-python-sdk"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "OpenAI"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("openai")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v("langtrace-python-sdk")
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.openai.com/v1/"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )
    assert attributes.get(SpanAttributes.LLM_RESPONSE_MODEL) == "gpt-4-0613"
    assert attributes.get(SpanAttributes.LLM_PROMPTS) == json.dumps(messages_value)
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is False

    assert_token_count(attributes)
    assert_response_format(attributes)


@pytest.mark.vcr()
def test_chat_completion_streaming(exporter, openai_client):
    llm_model_value = "gpt-4"
    messages_value = [{"role": "user", "content": "Say this is a test three times"}]

    kwargs = {
        "model": llm_model_value,
        "messages": messages_value,
        "stream": True,
    }

    chunk_count = 0
    response = openai_client.chat.completions.create(**kwargs)

    for _ in response:
        chunk_count += 1

    spans = exporter.get_finished_spans()
    streaming_span = spans[-1]

    assert streaming_span.name == "openai.chat.completions.create"
    attributes = streaming_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == "langtrace-python-sdk"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "OpenAI"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("openai")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v("langtrace-python-sdk")
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.openai.com/v1/"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )
    assert attributes.get(SpanAttributes.LLM_RESPONSE_MODEL) == "gpt-4-0613"
    assert attributes.get(SpanAttributes.LLM_PROMPTS) == json.dumps(messages_value)
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is True

    events = streaming_span.events
    assert len(events) - 2 == chunk_count  # -2 for start and end events

    assert_token_count(attributes)
    assert_response_format(attributes)

    langtrace_responses = json.loads(attributes.get(SpanAttributes.LLM_COMPLETIONS))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response

    langtrace_responses = json.loads(attributes.get(SpanAttributes.LLM_COMPLETIONS))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response


@pytest.mark.vcr()
@pytest.mark.asyncio()
async def test_async_chat_completion_streaming(exporter, async_openai_client):
    llm_model_value = "gpt-4"
    messages_value = [{"role": "user", "content": "Say this is a test three times"}]

    kwargs = {
        "model": llm_model_value,
        "messages": messages_value,
        "stream": True,
    }

    chunk_count = 0
    response = await async_openai_client.chat.completions.create(**kwargs)
    async for chunk in response:
        chunk_count += 1

    spans = exporter.get_finished_spans()
    streaming_span = spans[-1]

    assert streaming_span.name == "openai.chat.completions.create"
    attributes = streaming_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == "langtrace-python-sdk"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "OpenAI"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("openai")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v("langtrace-python-sdk")
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.openai.com/v1/"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    )
    assert attributes.get(SpanAttributes.LLM_RESPONSE_MODEL) == "gpt-4-0613"
    assert attributes.get(SpanAttributes.LLM_PROMPTS) == json.dumps(messages_value)
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is True

    events = streaming_span.events
    assert len(events) - 2 == chunk_count  # -2 for start and end events

    assert_token_count(attributes)
    assert_response_format(attributes)
