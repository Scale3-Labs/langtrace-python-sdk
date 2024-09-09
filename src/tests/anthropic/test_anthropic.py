import pytest
import json
import importlib
from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from tests.utils import (
    assert_completion_in_events,
    assert_langtrace_attributes,
    assert_prompt_in_events,
    assert_response_format,
    assert_token_count,
)
from importlib_metadata import version as v

from langtrace.trace_attributes import SpanAttributes


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

    anthropic_client.messages.create(**kwargs)
    spans = exporter.get_finished_spans()
    completion_span = spans[-1]

    assert completion_span.name == "anthropic.messages.create"
    attributes = completion_span.attributes
    assert_langtrace_attributes(attributes, "Anthropic")
    assert_prompt_in_events(completion_span.events)
    assert_completion_in_events(completion_span.events)
    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.anthropic.com"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["MESSAGES_CREATE"]["ENDPOINT"]
    )
    assert attributes.get(SpanAttributes.LLM_REQUEST_MODEL) == llm_model_value
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is False

    assert_token_count(attributes)


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

    assert_langtrace_attributes(attributes, "Anthropic")
    assert_prompt_in_events(streaming_span.events)
    assert_completion_in_events(streaming_span.events)

    assert attributes.get(SpanAttributes.LLM_URL) == "https://api.anthropic.com"
    assert (
        attributes.get(SpanAttributes.LLM_PATH) == APIS["MESSAGES_CREATE"]["ENDPOINT"]
    )
    assert attributes.get(SpanAttributes.LLM_REQUEST_MODEL) == llm_model_value
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is True

    assert_token_count(attributes)
