import pytest
from unittest.mock import Mock, patch
from langtrace_python_sdk.instrumentation.openai.patch import chat_completions_create
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper
from unittest.mock import MagicMock, patch, call
import importlib.metadata
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import openai
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode



def instrument():
        provider = TracerProvider()
        in_memory_exporter = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(in_memory_exporter))
        tracer = get_tracer(__name__, "", provider)
        version = importlib.metadata.version('openai')
        llm_model_value = 'gpt-4'
        # Define other required fields if any
        # For example:
        messages_value = [{'role': 'user', 'content': 'Say this is a test three times'}]

        # Create kwargs dictionary with valid values
        kwargs = {
            'model': llm_model_value,
            'messages': messages_value,
            'stream': False,  # Example value for stream, adjust as needed
            # Add other required fields with appropriate values
        }
        wrapped_function = chat_completions_create(openai.chat.completions.create, version, tracer)
        result = wrapped_function(None, (), {}, kwargs = kwargs)
        return result


print(instrument())


def test_chat_completions_create_non_streaming():
    # Mock dependencies
    provider = TracerProvider()
    in_memory_exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(in_memory_exporter))
    tracer = get_tracer(__name__, "", provider)
    version = importlib.metadata.version('openai')
    wrapped_method = Mock(return_value="mocked method result")
    instance = Mock()
    instance.name = "aa"
    llm_model_value = 'gpt-4'
    # Define other required fields if any
    # For example:
    messages_value = [{'role': 'user', 'content': 'Say this is a test three times'}]

        # Create kwargs dictionary with valid values
    kwargs = {
            'model': llm_model_value,
            'messages': messages_value,
            'stream': False,  # Example value for stream, adjust as needed
            # Add other required fields with appropriate values
    }
    wrapped_function = chat_completions_create(openai.chat.completions.create, version, tracer)
    result = wrapped_function(wrapped_method, instance, (), kwargs)
    # assert result == "mocked method result"
    assert result.system_fingerprint == None

'''
    # Assert that original method is called with correct arguments
    original_method.assert_called_once()

    # Assert span attributes
    tracer.start_span.assert_called_once_with(
        APIS["CHAT_COMPLETION"]["METHOD"], kind=SpanKind.CLIENT
    )
    expected_span_attributes = {
            "langtrace.service.name": 'openai',
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": 'chat/completions/create',
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.model": "gpt-4",
            "llm.stream": False,
            "llm.prompts": "[{'role': 'user', 'content': 'Say this is a test three times'}]"
        }
    span_set_attribute_calls = [call(field, value) for field, value in expected_span_attributes.items()]
    tracer.start_span.return_value.set_attribute.assert_has_calls(span_set_attribute_calls)
    tracer.start_span.return_value.set_status.assert_called_once_with(StatusCode.OK)
    tracer.start_span.return_value.end.assert_called_once()

    # Assert the return value
    assert result == original_method.return_value
'''