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
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["MESSAGES_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": prompts,
            "llm.stream": kwargs.get("stream"),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("top_p") is not None:
            attributes.llm_top_p = kwargs.get("top_p")
        if kwargs.get("top_k") is not None:
            attributes.llm_top_p = kwargs.get("top_k")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")
        if kwargs.get("max_tokens") is not None:
            attributes.llm_max_tokens = str(kwargs.get("max_tokens"))

        span = tracer.start_span(
            APIS["MESSAGES_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if kwargs.get("stream") is False:
                if hasattr(result, "content") and result.content is not None:
                    span.set_attribute(
                        "llm.model",
                        result.model if result.model else kwargs.get("model"),
                    )
                    span.set_attribute(
                        "llm.responses",
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
                    span.set_attribute("llm.responses", json.dumps(responses))
                if (
                    hasattr(result, "system_fingerprint")
                    and result.system_fingerprint is not None
                ):
                    span.set_attribute(
                        "llm.system.fingerprint", result.system_fingerprint
                    )
                # Get the usage
                if hasattr(result, "usage") and result.usage is not None:
                    usage = result.usage
                    if usage is not None:
                        usage_dict = {
                            "input_tokens": usage.input_tokens,
                            "output_tokens": usage.output_tokens,
                            "total_tokens": usage.input_tokens + usage.output_tokens,
                        }
                        span.set_attribute("llm.token.counts", json.dumps(usage_dict))
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
                    span.set_attribute("llm.model", chunk.message.model)
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
                "llm.token.counts",
                json.dumps(
                    {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                    }
                ),
            )
            span.set_attribute(
                "llm.responses",
                json.dumps([{"role": "assistant", "content": "".join(result_content)}]),
            )
            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
    return traced_method
