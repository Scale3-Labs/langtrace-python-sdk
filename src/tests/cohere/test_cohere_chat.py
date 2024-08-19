import json
from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
import pytest
import importlib
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


@pytest.mark.vcr
def test_cohere_chat(cohere_client, exporter):
    llm_model_value = "command"
    messages_value = "Tell me a story in 3 sentences or less?"
    preamble_value = "answer like a pirate"
    connectors = [{"id": "web-search"}]
    kwargs = {
        "model": llm_model_value,
        "message": messages_value,
        "preamble": preamble_value,
        "connectors": connectors,
        "temperature": 0.1,
        "chat_history": [
            {"role": "USER", "message": "Who discovered gravity?"},
            {
                "role": "CHATBOT",
                "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton",
            },
        ],
    }
    res = cohere_client.chat(**kwargs)
    spans = exporter.get_finished_spans()
    cohere_span = spans[-1]
    assert cohere_span.name == APIS["CHAT_CREATE"]["METHOD"]
    attributes = cohere_span.attributes
    assert_langtrace_attributes(attributes, SERVICE_PROVIDERS["COHERE"])
    assert_prompt_in_events(cohere_span.events)
    assert_completion_in_events(cohere_span.events)

    assert attributes.get(SpanAttributes.LLM_URL) == APIS["CHAT_CREATE"]["URL"]
    assert attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_CREATE"]["ENDPOINT"]
    assert attributes.get(SpanAttributes.LLM_REQUEST_MODEL) == llm_model_value
    assert attributes.get(SpanAttributes.LLM_REQUEST_TEMPERATURE) == kwargs.get(
        "temperature"
    )
    assert attributes.get(SpanAttributes.LLM_GENERATION_ID) == res.generation_id

    assert json.loads(attributes.get("llm_connectors")) == connectors

    assert_token_count(attributes)


@pytest.mark.vcr
def test_cohere_chat_streaming(cohere_client, exporter):
    llm_model_value = "command"
    messages_value = "Tell me a story in 3 sentences or less?"
    preamble_value = "answer like a pirate"
    connectors = [{"id": "web-search"}]
    kwargs = {
        "model": llm_model_value,
        "message": messages_value,
        "preamble": preamble_value,
        "connectors": connectors,
        "temperature": 0.1,
        "chat_history": [
            {"role": "USER", "message": "Who discovered gravity?"},
            {
                "role": "CHATBOT",
                "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton",
            },
        ],
    }

    res = cohere_client.chat_stream(**kwargs)

    chunks_count = 0
    streamed_response = ""
    for chunk in res:
        if chunk.event_type == "text-generation":
            streamed_response += chunk.text
        chunks_count += 1

    spans = exporter.get_finished_spans()
    cohere_span = spans[-1]
    assert cohere_span.name == APIS["CHAT_STREAM"]["METHOD"]
    attributes = cohere_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME
    assert (
        attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME)
        == SERVICE_PROVIDERS["COHERE"]
    )
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("cohere")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == APIS["CHAT_STREAM"]["URL"]
    assert attributes.get(SpanAttributes.LLM_PATH) == APIS["CHAT_STREAM"]["ENDPOINT"]
    assert attributes.get(SpanAttributes.LLM_REQUEST_MODEL) == llm_model_value
    assert attributes.get(SpanAttributes.LLM_REQUEST_TEMPERATURE) == kwargs.get(
        "temperature"
    )
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is True

    assert json.loads(attributes.get("llm_connectors")) == connectors
    events = cohere_span.events
    assert_prompt_in_events(events)
    assert_completion_in_events(events)

    assert_token_count(attributes)
