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

from typing import Any, Callable, List, Iterator, Union
from langtrace.trace_attributes import SpanAttributes, LLMSpanAttributes
import json

from langtrace_python_sdk.utils.llm import (
    StreamWrapper,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    set_span_attributes,
    set_usage_attributes,
    set_span_attribute,
)
from opentelemetry.trace import Span, Tracer, SpanKind
from opentelemetry.trace.status import StatusCode
from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.instrumentation.anthropic.types import (
    StreamingResult,
    ResultType,
    MessagesCreateKwargs,
)


def messages_create(version: str, tracer: Tracer) -> Callable[..., Any]:
    """Wrap the `messages_create` method."""

    def traced_method(
        wrapped: Callable[..., Any],
        instance: Any,
        args: List[Any],
        kwargs: MessagesCreateKwargs,
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["ANTHROPIC"]

        # Extract system from kwargs and attach as a role to the prompts
        prompts = kwargs.get("messages", [])
        system = kwargs.get("system")
        if system:
            prompts.append({"role": "system", "content": system})
        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["MESSAGES_CREATE"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["MESSAGES_CREATE"]["METHOD"]), kind=SpanKind.CLIENT
        )
        
        set_span_attributes(span, attributes)
        
        tools = []
        if kwargs.get("tools") is not None and kwargs.get("tools"):
            tools.append(json.dumps(kwargs.get("tools")))
            set_span_attribute(span, SpanAttributes.LLM_TOOLS, json.dumps(tools))

        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            return set_response_attributes(result, span)

        except Exception as err:
            # Record the exception in the span
            span.record_exception(err)
            # Set the span status to indicate an error
            span.set_status(StatusCode.ERROR, str(err))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    def set_response_attributes(
        result: Union[ResultType, StreamingResult], span: Span
    ) -> Any:
        if not isinstance(result, Iterator):
            if hasattr(result, "content") and result.content is not None:
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, result.model
                )
                if hasattr(result, "content") and result.content[0] is not None:
                    content = result.content[0]
                    typ = content.type
                    role = result.role if result.role else "assistant"
                    if typ == "tool_result" or typ == "tool_use":
                        content = content.json()  # type: ignore
                        set_span_attribute(
                            span, SpanAttributes.LLM_TOOL_RESULTS, json.dumps(content)
                        )
                    if typ == "text":
                        content = result.content[0].text
                        set_event_completion(
                            span, [{"type": typ, "role": role, "content": content}]
                        )

            if (
                hasattr(result, "system_fingerprint")
                and result.system_fingerprint is not None
            ):
                span.set_attribute(
                    SpanAttributes.LLM_SYSTEM_FINGERPRINT,
                    result.system_fingerprint,
                )
            # Get the usage
            if hasattr(result, "usage") and result.usage is not None:
                usage = result.usage
                set_usage_attributes(span, vars(usage))

            span.set_status(StatusCode.OK)
            span.end()
            return result
        else:
            return StreamWrapper(result, span, tool_calls=True)

    # return the wrapped method
    return traced_method


def messages_stream(version: str, tracer: Tracer) -> Callable[..., Any]:

    def traced_method(
        wrapped: Callable[..., Any],
        instance: Any,
        args: List[Any],
        kwargs: MessagesCreateKwargs,
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["ANTHROPIC"]

        prompts = kwargs.get("messages", [])
        system = kwargs.get("system")
        if system:
            prompts.append({"role": "assistant", "content": system})
        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["MESSAGES_STREAM"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["MESSAGES_STREAM"]["METHOD"]), kind=SpanKind.CLIENT
        )
        
        set_span_attributes(span, attributes)
        
        tools = []
        if kwargs.get("tools") is not None:
            tools.append(json.dumps(kwargs.get("tools")))
            set_span_attribute(span, SpanAttributes.LLM_TOOLS, json.dumps(tools))
            
        try:
            # Create the original message stream manager
            original_stream_manager = wrapped(*args, **kwargs)
            
            # Create a new stream manager that will instrument the stream
            # while preserving the stream
            class InstrumentedMessageStreamManager:
                def __init__(self, original_manager, span):
                    self.original_manager = original_manager
                    self.span = span
                
                def __enter__(self):
                    # Enter the original context manager to get the stream
                    original_stream = self.original_manager.__enter__()
                    
                    # Create a wrapper iterator
                    class InstrumentedStream:
                        def __init__(self, original_stream, span):
                            self.original_stream = original_stream
                            self.span = span
                            self.message_stop_processed = False
                        
                        def __iter__(self):
                            return self
                        
                        def __next__(self):
                            try:
                                chunk = next(self.original_stream)
                                
                                # Apply instrumentation only once on message_stop
                                if chunk.type == "message_stop" and not self.message_stop_processed:
                                    self.message_stop_processed = True
                                    response_message = chunk.message
                                        
                                    responses = [
                                        {
                                            "role": (
                                                response_message.role
                                                if response_message.role
                                                else "assistant"
                                            ),
                                            "content": message.text,
                                        }
                                        for message in response_message.content if message.type == "text"
                                    ]
                                    
                                    set_event_completion(self.span, responses)
                                    
                                    if hasattr(response_message, "usage") and response_message.usage is not None:
                                        set_span_attribute(
                                            self.span,
                                            SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                                            response_message.usage.input_tokens,
                                        )
                                        set_span_attribute(
                                            self.span,
                                            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                                            response_message.usage.output_tokens,
                                        )
                                        set_span_attribute(
                                            self.span,
                                            SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                                            response_message.usage.input_tokens + response_message.usage.output_tokens,
                                        )
                                
                                # Forward the chunk
                                return chunk
                            except StopIteration:
                                # End the span when we're done with the stream
                                self.span.end()
                                raise
                            except Exception as err:
                                self.span.record_exception(err)
                                self.span.set_status(StatusCode.ERROR, str(err))
                                self.span.end()
                                raise
                        
                        def close(self):
                            self.original_stream.close()
                            if not self.message_stop_processed:
                                self.span.end()
                    
                    # Return our instrumented stream wrapper
                    return InstrumentedStream(original_stream, self.span)
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    result = self.original_manager.__exit__(exc_type, exc_val, exc_tb)

                    if exc_type is not None:
                        self.span.record_exception(exc_val)
                        self.span.set_status(StatusCode.ERROR, str(exc_val))
                        self.span.end()
                    
                    return result
            
            # Return the instrumented stream manager
            return InstrumentedMessageStreamManager(original_stream_manager, span)

        except Exception as err:
            span.record_exception(err)
            span.set_status(StatusCode.ERROR, str(err))
            span.end()
            raise

    return traced_method
