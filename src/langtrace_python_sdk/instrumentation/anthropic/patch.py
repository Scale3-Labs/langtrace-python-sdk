"""
Copyright (c) 2024 Scale3 Labs

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json

from langtrace.trace_attributes import Event, LLMSpanAttributes
from langtrace_python_sdk.utils import set_span_attribute
from opentelemetry import baggage
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace.trace_attributes import SpanAttributes


def messages_create(original_method, version, tracer):
    """Wrap the `messages_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["ANTHROPIC"]

        # extract system from kwargs and attach as a role to the prompts
        # we do this to keep it consistent with the openai
        prompts = json.dumps(kwargs.get("messages", []))
        system = kwargs.get("system")
        if system:
            prompts = json.dumps(
                [{"role": "system", "content": system}] + kwargs.get("messages", [])
            )
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            SpanAttributes.LANGTRACE_SDK_NAME.value: LANGTRACE_SDK_NAME,
            SpanAttributes.LANGTRACE_SERVICE_NAME.value: service_provider,
            SpanAttributes.LANGTRACE_SERVICE_TYPE.value: "llm",
            SpanAttributes.LANGTRACE_SERVICE_VERSION.value: version,
            SpanAttributes.LANGTRACE_VERSION.value: v(LANGTRACE_SDK_NAME),
            SpanAttributes.LLM_URL.value: base_url,
            SpanAttributes.LLM_PATH.value: APIS["MESSAGES_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_MODEL.value: kwargs.get("model"),
            SpanAttributes.LLM_PROMPTS.value: prompts,
            SpanAttributes.LLM_IS_STREAMING.value: kwargs.get("stream"),
            SpanAttributes.LLM_REQUEST_TEMPERATURE.value: kwargs.get("temperature"),
            SpanAttributes.LLM_REQUEST_TOP_P.value: kwargs.get("top_p"),
            SpanAttributes.LLM_TOP_K.value: kwargs.get("top_k"),
            SpanAttributes.LLM_USER.value: kwargs.get("user"),
            SpanAttributes.LLM_REQUEST_MAX_TOKENS.value: str(kwargs.get("max_tokens")),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            APIS["MESSAGES_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if kwargs.get("stream") is False:
                if hasattr(result, "content") and result.content is not None:
                    span.set_attribute(
                        SpanAttributes.LLM_RESPONSE_MODEL.value,
                        result.model if result.model else kwargs.get("model"),
                    )
                    span.set_attribute(
                        SpanAttributes.LLM_COMPLETIONS.value,
                        json.dumps(
                            [
                                {
                                    "role": result.role if result.role else "assistant",
                                    "content": result.content[0].text,
                                    "type": result.content[0].type,
                                }
                            ]
                        ),
                    )
                else:
                    responses = []
                    span.set_attribute(
                        SpanAttributes.LLM_COMPLETIONS.value, json.dumps(responses)
                    )
                if (
                    hasattr(result, "system_fingerprint")
                    and result.system_fingerprint is not None
                ):
                    span.set_attribute(
                        SpanAttributes.LLM_SYSTEM_FINGERPRINT.value,
                        result.system_fingerprint,
                    )
                # Get the usage
                if hasattr(result, "usage") and result.usage is not None:
                    usage = result.usage
                    if usage is not None:
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value,
                            usage.output_tokens,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value,
                            usage.input_tokens,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
                            usage.input_tokens + usage.output_tokens,
                        )

                span.set_status(StatusCode.OK)
                span.end()
                return result
            else:
                return handle_streaming_response(result, span)
        except Exception as err:
            # Record the exception in the span
            span.record_exception(err)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(err)))
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
                if (
                    hasattr(chunk, "message")
                    and chunk.message is not None
                    and hasattr(chunk.message, "model")
                    and chunk.message.model is not None
                ):
                    span.set_attribute(
                        SpanAttributes.LLM_RESPONSE_MODEL.value, chunk.message.model
                    )
                content = ""
                if hasattr(chunk, "delta") and chunk.delta is not None:
                    content = chunk.delta.text if hasattr(chunk.delta, "text") else ""
                # Assuming content needs to be aggregated before processing
                result_content.append(content if len(content) > 0 else "")

                if hasattr(chunk, "message") and hasattr(chunk.message, "usage"):
                    input_tokens += (
                        chunk.message.usage.input_tokens
                        if hasattr(chunk.message.usage, "input_tokens")
                        else 0
                    )
                    output_tokens += (
                        chunk.message.usage.output_tokens
                        if hasattr(chunk.message.usage, "output_tokens")
                        else 0
                    )

                # Assuming span.add_event is part of a larger logging or event system
                # Add event for each chunk of content
                if content:
                    span.add_event(
                        Event.STREAM_OUTPUT.value, {"response": "".join(content)}
                    )

                # Assuming this is part of a generator, yield chunk or aggregated content
                yield content
        finally:

            # Finalize span after processing all chunks
            span.add_event(Event.STREAM_END.value)
            span.set_attribute(
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value, input_tokens
            )
            span.set_attribute(
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value, output_tokens
            )
            span.set_attribute(
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
                input_tokens + output_tokens,
            )

            span.set_attribute(
                SpanAttributes.LLM_COMPLETIONS.value,
                json.dumps([{"role": "assistant", "content": "".join(result_content)}]),
            )
            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
    return traced_method
