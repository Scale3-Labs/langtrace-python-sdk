import pytest
from unittest.mock import patch
import openai
from langtrace.trace_attributes import Event, LLMSpanAttributes
from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())
def capital_case(x):
    return x.capitalize()
def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'
@pytest.fixture
def openai_mock():
    with patch('openai.chat.completions.create') as mock_chat_completion:
        mock_chat_completion.return_value = {"choices": [{"text": "This is a test. This is test. This is a test."}]}
        yield mock_chat_completion
def test_completion():
        from langtrace_python_sdk import langtrace
        exporter = langtrace.init(batch=False, log_spans_to_console=False,
        write_to_remote_url=False, log_spans_in_memory=True)
        openai.OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
        )
        spans = exporter.get_finished_spans()
        open_ai_span = spans[0]
        attributes = open_ai_span.attributes
        print("here...")
        print(open_ai_span.attributes)
        service_provider = 'openai'
        
        # attributes = OpenAISpanAttributes(**span_attributes)
        other_fields = ['langtrace.service.name', 'langtrace.service.type', 'langtrace.service.version', 'langtrace.version', 'url.full', 'llm.api', 'llm.model', 'llm.prompts', 'llm.stream', 'llm.responses', 'llm.token.counts']
        optional_fields = ['llm.temperature', 'llm.top_p', 'llm.user', 'llm.system.fingerprint', 'http.max.retries', 'http.timeout', 'llm.responses', 'llm.token.counts', 'llm.encoding.format', 'llm.dimensions']
        # assert len(spans) == 0
        for key in open_ai_span.attributes:
            try:
                print(key, other_fields.index(key))
                assert(key, other_fields.index(key))
            except KeyError:
                print(f"Attribute '{key}' not found in open_ai_span.attributes")
        service_provider = SERVICE_PROVIDERS['OPENAI']
        span_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": '1.12.0',
            "langtrace.version": "1.0.0",
            "url.full": 'chat/completions/create',
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": 'gpt-4',
            "llm.prompts": '[{"role": "user", "content": "Say this is a test three times"}]',
            "llm.stream": False,
        }
        attributes = LLMSpanAttributes(**span_attributes)
        for key, value in attributes.model_dump(by_alias=True).items():
                try:
                    if key not in optional_fields:
                        assert(key, open_ai_span.attributes.get(key) == value)
                except KeyError:
                    # Handle the KeyError (attribute not found in open_ai_span.attributes)
                    print(f"Attribute '{key}' not found in open_ai_span.attributes")


