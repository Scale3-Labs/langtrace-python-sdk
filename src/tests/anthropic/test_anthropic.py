import pytest
import json
import importlib
from langtrace_python_sdk.constants.instrumentation.anthropic import APIS


@pytest.mark.vcr()
def test_anthropic(anthropic_client, exporter):
    llm_model_value = "claude-3-opus-20240229"
    messages_value = [{"role": "user", "content": "How are you today?"}]

    kwargs = {
        "model": llm_model_value,
        "messages": messages_value,
        # "system": "Respond only in Yoda-speak.",
        "stream": False,
        "max_tokens": 1024,
    }
    response = anthropic_client.messages.create(**kwargs)
    spans = exporter.get_finished_spans()
    completion_span = spans[-1]

    assert completion_span.name == "anthropic.messages.create"
    attributes = completion_span.attributes

    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "Anthropic"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == importlib.metadata.version(
        "anthropic"
    )
    assert attributes.get("langtrace.version") == "1.0.0"
    assert attributes.get("url.full") == "https://api.anthropic.com"
    assert attributes.get("llm.api") == APIS["MESSAGES_CREATE"]["ENDPOINT"]
    assert attributes.get("llm.model") == llm_model_value
    assert attributes.get("llm.prompts") == json.dumps(messages_value)
    assert attributes.get("llm.stream") is False

    tokens = json.loads(attributes.get("llm.token.counts"))
    output_tokens = tokens.get("output_tokens")
    prompt_tokens = tokens.get("input_tokens")
    total_tokens = tokens.get("total_tokens")

    assert output_tokens and prompt_tokens and total_tokens
    assert output_tokens + prompt_tokens == total_tokens

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response


@pytest.mark.vcr()
def test_anthropic_streaming(anthropic_client, exporter):
    llm_model_value = "claude-3-opus-20240229"
    messages_value = [{"role": "user", "content": "How are you today?"}]

    kwargs = {
        "model": llm_model_value,
        "messages": messages_value,
        # "system": "Respond only in Yoda-speak.",
        "stream": True,
        "max_tokens": 1024,
    }
    response = anthropic_client.messages.create(**kwargs)
    chunk_count = 0

    for chunk in response:
        if chunk:
            chunk_count += 1

    spans = exporter.get_finished_spans()
    streaming_span = spans[-1]

    assert streaming_span.name == "anthropic.messages.create"
    attributes = streaming_span.attributes

    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == "Anthropic"
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == importlib.metadata.version(
        "anthropic"
    )
    assert attributes.get("langtrace.version") == "1.0.0"
    assert attributes.get("url.full") == "https://api.anthropic.com"
    assert attributes.get("llm.api") == APIS["MESSAGES_CREATE"]["ENDPOINT"]
    assert attributes.get("llm.model") == llm_model_value
    assert attributes.get("llm.prompts") == json.dumps(messages_value)
    assert attributes.get("llm.stream") is True
    events = streaming_span.events

    assert len(events) - 2 == chunk_count  # -2 for start and end events

    tokens = json.loads(attributes.get("llm.token.counts"))
    output_tokens = tokens.get("output_tokens")
    prompt_tokens = tokens.get("input_tokens")
    total_tokens = tokens.get("total_tokens")

    assert output_tokens and prompt_tokens and total_tokens
    assert output_tokens + prompt_tokens == total_tokens

    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response
