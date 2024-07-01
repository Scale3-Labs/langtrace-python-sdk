from unittest.mock import MagicMock, patch
import json
from langtrace.trace_attributes import SpanAttributes


def common_setup(data, method_to_mock=None):
    if method_to_mock:
        service_mock = patch(method_to_mock)
        mock_method = service_mock.start()
        mock_method.return_value = json.dumps(data)
    else:
        service_mock = MagicMock()
        service_mock.return_value = MagicMock(**data)

    tracer = MagicMock()
    span = MagicMock()

    context_manager_mock = MagicMock()
    context_manager_mock.__enter__.return_value = span
    tracer.start_as_current_span.return_value = context_manager_mock

    return service_mock, tracer, span


def assert_token_count(attributes):
    output_tokens = attributes.get(SpanAttributes.LLM_USAGE_COMPLETION_TOKENS)
    prompt_tokens = attributes.get(SpanAttributes.LLM_USAGE_PROMPT_TOKENS)
    total_tokens = attributes.get(SpanAttributes.LLM_USAGE_TOTAL_TOKENS)

    assert (
        output_tokens is not None
        and prompt_tokens is not None
        and total_tokens is not None
    )
    assert output_tokens + prompt_tokens == total_tokens


def assert_response_format(attributes):

    langtrace_responses = json.loads(attributes.get(SpanAttributes.LLM_COMPLETIONS))

    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response
