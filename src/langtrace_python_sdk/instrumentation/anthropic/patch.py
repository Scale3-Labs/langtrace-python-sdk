"""
This module contains the patching logic for the Anthropic library."""
import json

from langtrace.trace_attributes import Event, LLMSpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS
from langtrace_python_sdk.utils.llm import estimate_tokens


def messages_create(original_method, version, tracer):
    """Wrap the `messages_create` method."""
    def traced_method(wrapped, instance, args, kwargs):
        base_url = str(instance._client._base_url) if hasattr(
            instance, '_client') and hasattr(instance._client, '_base_url') else ""
        service_provider = SERVICE_PROVIDERS['ANTHROPIC']
        span_attributes = {
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": "1.0.0",
            "url.full": base_url,
            "llm.api": APIS["MESSAGES_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get('model'),
            "llm.prompts": json.dumps(kwargs.get('messages', [])),
            "llm.stream": kwargs.get('stream'),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get('temperature') is not None:
            attributes.llm_temperature = kwargs.get('temperature')
        if kwargs.get('top_p') is not None:
            attributes.llm_top_p = kwargs.get('top_p')
        if kwargs.get('top_k') is not None:
            attributes.llm_top_p = kwargs.get('top_k')
        if kwargs.get('user') is not None:
            attributes.llm_user = kwargs.get('user')

        span = tracer.start_span(
            APIS["MESSAGES_CREATE"]["METHOD"], kind=SpanKind.CLIENT)
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if kwargs.get('stream') is False:
                if hasattr(result, 'content') and result.content is not None:
                    span.set_attribute(
                        "llm.responses", json.dumps([{
                            "text": result.content[0].text,
                            "type": result.content[0].type
                        }]))
                else:
                    responses = []
                    span.set_attribute(
                        "llm.responses", json.dumps(responses))
                if hasattr(result, 'system_fingerprint') and \
                        result.system_fingerprint is not None:
                    span.set_attribute(
                        "llm.system.fingerprint", result.system_fingerprint)
                # Get the usage
                if hasattr(result, 'usage') and result.usage is not None:
                    usage = result.usage
                    if usage is not None:
                        usage_dict = {
                            "input_tokens": usage.input_tokens,
                            "output_tokens": usage.output_tokens,
                            "total_tokens": usage.input_tokens + usage.output_tokens
                        }
                        span.set_attribute(
                            "llm.token.counts", json.dumps(usage_dict))
                span.set_status(StatusCode.OK)
                span.end()
                return result
            else:
                return handle_streaming_response(result, span)
        except Exception as e:
            # Record the exception in the span
            span.record_exception(e)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    def handle_streaming_response(result, span):
        """Process and yield streaming response chunks."""
        result_content = []
        span.add_event(Event.STREAM_START.value)
        input_tokens = 0
        output_tokens = 0
        try:
            for chunk in result:
                content = ""
                if hasattr(chunk, 'delta') and chunk.delta is not None:
                    content = chunk.delta.text if hasattr(
                        chunk.delta, 'text') else ""
                # Assuming content needs to be aggregated before processing
                result_content.append(content if len(content) > 0 else "")

                if hasattr(chunk, 'message') and hasattr(chunk.message, 'usage'):
                    input_tokens += chunk.message.usage.input_tokens if hasattr(
                        chunk.message.usage, 'input_tokens') else 0
                    output_tokens += chunk.message.usage.output_tokens if hasattr(
                        chunk.message.usage, 'output_tokens') else 0

                # Assuming span.add_event is part of a larger logging or event system
                # Add event for each chunk of content
                if content:
                    span.add_event(Event.STREAM_OUTPUT.value, {
                        "response": "".join(content)
                    })

                # Assuming this is part of a generator, yield chunk or aggregated content
                yield content
        finally:

            # Finalize span after processing all chunks
            span.add_event(Event.STREAM_END.value)
            span.set_attribute("llm.token.counts", json.dumps({
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }))
            span.set_attribute("llm.responses", json.dumps(
                [{"text": "".join(result_content)}]))
            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
    return traced_method
