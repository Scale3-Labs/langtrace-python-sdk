import pytest
import json
from tests.utils import (
    assert_completion_in_events,
    assert_prompt_in_events,
    assert_token_count,
)
from importlib_metadata import version as v
from langtrace.trace_attributes import SpanAttributes
from langtrace_python_sdk.constants.instrumentation.aws_bedrock import APIS

ANTHROPIC_VERSION = "bedrock-2023-05-31"


@pytest.mark.vcr()
def test_chat_completion(exporter, aws_bedrock_client):
    model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    messages_value = [{"role": "user", "content": "Say this is a test three times"}]

    kwargs = {
        "modelId": model_id,
        "accept": "application/json",
        "contentType": "application/json",
        "body": json.dumps(
            {
                "messages": messages_value,
                "anthropic_version": ANTHROPIC_VERSION,
                "max_tokens": 100,
            }
        ),
    }

    aws_bedrock_client.invoke_model(**kwargs)
    spans = exporter.get_finished_spans()
    completion_span = spans[-1]
    assert completion_span.name == "aws_bedrock.invoke_model"

    attributes = completion_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == "langtrace-python-sdk"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "anthropic"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "framework"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("boto3")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v("langtrace-python-sdk")
    assert attributes.get(SpanAttributes.LLM_PATH) == APIS["INVOKE_MODEL"]["ENDPOINT"]
    assert attributes.get(SpanAttributes.LLM_RESPONSE_MODEL) == model_id
    assert_prompt_in_events(completion_span.events)
    assert_completion_in_events(completion_span.events)
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is False

    assert_token_count(attributes)


@pytest.mark.vcr()
def test_generate_embedding(exporter, aws_bedrock_client):
    model_id = "amazon.titan-embed-text-v1"

    kwargs = {
        "modelId": model_id,
        "accept": "application/json",
        "contentType": "application/json",
        "body": json.dumps(
            {
                "inputText": "Say this is a test three times",
            }
        ),
    }

    aws_bedrock_client.invoke_model(**kwargs)
    spans = exporter.get_finished_spans()
    completion_span = spans[-1]
    assert completion_span.name == "aws_bedrock.invoke_model"

    attributes = completion_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == "langtrace-python-sdk"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME) == "amazon"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "framework"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("boto3")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v("langtrace-python-sdk")
    assert attributes.get(SpanAttributes.LLM_PATH) == APIS["INVOKE_MODEL"]["ENDPOINT"]
    assert attributes.get(SpanAttributes.LLM_RESPONSE_MODEL) == model_id
    assert_prompt_in_events(completion_span.events)
    assert attributes.get(SpanAttributes.LLM_IS_STREAMING) is False

    assert_token_count(attributes)
