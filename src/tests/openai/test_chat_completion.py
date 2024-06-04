import pytest
import json
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from tests.utils import assert_response_format, assert_token_count
from importlib_metadata import version as v


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
    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "OpenAI"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == v("openai")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("url.full") == "https://api.openai.com/v1/"
    assert attributes.get("llm.api") == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    assert attributes.get("llm.model") == "gpt-4-0613"
    assert attributes.get("llm.prompts") == json.dumps(messages_value)
    assert attributes.get("llm.stream") is False

    assert_token_count(attributes)
    assert_response_format(attributes)

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response


@pytest.mark.vcr()
def test_chat_completion_streaming(exporter, openai_client):
    llm_model_value = "gpt-4"
    messages_value = [{"role": "user", "content": "Say this is a test three times"}]

    kwargs = {
        "model": llm_model_value,
        "messages": messages_value,
        "stream": True,
    }

    response = openai_client.chat.completions.create(**kwargs)
    chunk_count = 0
    for _ in response:
        chunk_count += 1

    spans = exporter.get_finished_spans()
    streaming_span = spans[-1]

    assert streaming_span.name == "openai.chat.completions.create"
    attributes = streaming_span.attributes

    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "OpenAI"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == v("openai")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("url.full") == "https://api.openai.com/v1/"
    assert attributes.get("llm.api") == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    assert attributes.get("llm.model") == "gpt-4-0613"
    assert attributes.get("llm.prompts") == json.dumps(messages_value)
    assert attributes.get("llm.stream") is True

    events = streaming_span.events
    assert len(events) - 2 == chunk_count  # -2 for start and end events

    assert_token_count(attributes)
    assert_response_format(attributes)

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response

    langtrace_responses = json.loads(attributes.get("llm.responses"))
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

    response = await async_openai_client.chat.completions.create(**kwargs)
    chunk_count = 0
    async for _ in response:
        chunk_count += 1

    spans = exporter.get_finished_spans()
    streaming_span = spans[-1]

    assert streaming_span.name == "openai.chat.completions.create"
    attributes = streaming_span.attributes

    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "OpenAI"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == v("openai")
    assert attributes.get("langtrace.version") == v("langtrace-python-sdk")
    assert attributes.get("url.full") == "https://api.openai.com/v1/"
    assert attributes.get("llm.api") == APIS["CHAT_COMPLETION"]["ENDPOINT"]
    assert attributes.get("llm.model") == "gpt-4-0613"
    assert attributes.get("llm.prompts") == json.dumps(messages_value)
    assert attributes.get("llm.stream") is True

    events = streaming_span.events
    assert len(events) - 2 == chunk_count  # -2 for start and end events

    assert_token_count(attributes)
    assert_response_format(attributes)
