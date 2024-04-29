from unittest.mock import MagicMock, patch
import json


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
    tokens = json.loads(attributes.get("llm.token.counts"))
    output_tokens = tokens.get("output_tokens")
    prompt_tokens = tokens.get("input_tokens")
    total_tokens = tokens.get("total_tokens")

    assert (
        output_tokens is not None
        and prompt_tokens is not None
        and total_tokens is not None
    )
    assert output_tokens + prompt_tokens == total_tokens


def assert_response_format(attributes):
    langtrace_responses = json.loads(attributes.get("llm.responses"))
    assert isinstance(langtrace_responses, list)
    for langtrace_response in langtrace_responses:
        assert isinstance(langtrace_response, dict)
        assert "role" in langtrace_response
        assert "content" in langtrace_response
