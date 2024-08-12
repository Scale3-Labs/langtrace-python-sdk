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

from typing import Any, Callable, Dict, List, Optional, Iterator, TypedDict, Union
from langtrace.trace_attributes import Event, SpanAttributes, LLMSpanAttributes
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    set_event_completion,
    set_event_completion_chunk,
    set_usage_attributes,
    set_span_attribute
)
from opentelemetry.trace import Span, Tracer, SpanKind
from opentelemetry.trace.status import StatusCode
from src.langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from src.langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from src.langtrace_python_sdk.instrumentation.anthropic.types import StreamingResult, ResultType, MessagesCreateKwargs, ContentItem, Usage

def handle_streaming_response(result: StreamingResult, span: Span) -> Iterator[str]:
    result_content: List[str] = []
    span.add_event(Event.STREAM_START.value)
    input_tokens: int = 0
    output_tokens: int = 0
    try:
        for chunk in result:
            if chunk['message']["model"] is not None:
                span.set_attribute(
                    SpanAttributes.LLM_RESPONSE_MODEL, chunk["message"]["model"]
                )
            content: str = ""
            if chunk["delta"].get("text") is not None:
                content = chunk["delta"]["text"] or ""
            result_content.append(content if len(content) > 0 else "")

            if chunk["message"]["usage"] is not None:
                usage = chunk["message"]["usage"]
                input_tokens += usage.get("input_tokens", 0)
                output_tokens += usage.get("output_tokens", 0)

            if content:
                set_event_completion_chunk(span, "".join(content))

            yield content
    finally:
        span.add_event(Event.STREAM_END.value)
        set_usage_attributes(
            span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
        )
        completion: List[Dict[str, str]] = [{"role": "assistant", "content": "".join(result_content)}]
        set_event_completion(span, completion)

        span.set_status(StatusCode.OK)
        span.end()

def messages_create(version: str, tracer: Tracer) -> Callable[..., Any]:
    """Wrap the `messages_create` method."""

    def traced_method(wrapped: Callable[..., Any], instance: Any, args: List[Any], kwargs: MessagesCreateKwargs) -> Any:
        service_provider = SERVICE_PROVIDERS["ANTHROPIC"]

        # Extract system from kwargs and attach as a role to the prompts
        prompts = kwargs.get("messages", [])
        system = kwargs.get("system")
        if system:
            prompts = [{"role": "system", "content": system}] + kwargs.get("messages", [])
        extraAttributes = get_extra_attributes()
        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["MESSAGES_CREATE"]["ENDPOINT"],
            **extraAttributes,
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
            return set_response_attributes(result, span, kwargs)

        except Exception as err:
            # Record the exception in the span
            span.record_exception(err)
            # Set the span status to indicate an error
            span.set_status(StatusCode.ERROR, str(err))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    def handle_streaming_response(result: StreamingResult, span: Span) -> Iterator[str]:
        """Process and yield streaming response chunks."""
        result_content: List[str] = []
        span.add_event(Event.STREAM_START.value)
        input_tokens: int = 0
        output_tokens: int = 0
        try:
            for chunk in result:
                span.set_attribute(
                    SpanAttributes.LLM_RESPONSE_MODEL, chunk["message"]["model"] or ""
                )
                content: str = ""
                if hasattr(chunk, "delta") and chunk["delta"] is not None:
                    content = chunk["delta"]["text"] or ""
                result_content.append(content if len(content) > 0 else "")
                if chunk["message"]["usage"] is not None:
                    input_tokens += (
                        chunk["message"]["usage"]["input_tokens"]
                        if hasattr(chunk["message"]["usage"], "input_tokens")
                        else 0
                    )
                    output_tokens += (
                        chunk["message"]["usage"]["output_tokens"]
                        if hasattr(chunk["message"]["usage"], "output_tokens")
                        else 0
                    )

                if content:
                    set_event_completion_chunk(span, "".join(content))

                yield content
        finally:
            span.add_event(Event.STREAM_END.value)
            set_usage_attributes(
                span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
            )
            completion = [{"role": "assistant", "content": "".join(result_content)}]
            set_event_completion(span, completion)

            span.set_status(StatusCode.OK)
            span.end()

    def set_response_attributes(result: Union[ResultType, StreamingResult], span: Span, kwargs: MessagesCreateKwargs) -> Any:
        if not isinstance(result, Iterator):
            if result["content"] is not None:
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, result["model"]
                )
                content_item = result["content"][0]
                completion: List[ContentItem] = [
                    {
                        "role": result["role"] or "assistant",
                        "content": content_item.get("text", ""),
                        "type": content_item.get("type", ""),
                    }
                ]
                set_event_completion(span, completion)

            else:
                responses: List[ContentItem] = []
                set_event_completion(span, responses)

            if result["system_fingerprint"] is not None:
                span.set_attribute(
                    SpanAttributes.LLM_SYSTEM_FINGERPRINT,
                    result["system_fingerprint"],
                )
            # Get the usage
            if result["usage"] is not None:
                usage: Usage = result["usage"]
                set_usage_attributes(span, dict(usage))

            span.set_status(StatusCode.OK)
            span.end()
            return result
        else:
            return handle_streaming_response(result, span)

    # return the wrapped method
    return traced_method
