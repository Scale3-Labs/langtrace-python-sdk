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

from langtrace.trace_attributes import (
    Event,
    LLMSpanAttributes,
    SpanAttributes,
)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from langtrace_python_sdk.utils.llm import (
    calculate_prompt_tokens,
    estimate_tokens,
    get_base_url,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_tool_calls,
    is_streaming,
    set_event_completion,
)
from openai._types import NOT_GIVEN
from opentelemetry.trace.span import Span


def images_generate(original_method, version, tracer):
    """
    Wrap the `generate` method of the `Images` class to trace it.
    """

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_GENERATION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_GENERATION"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                set_span_attribute(span, field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                if not is_streaming(kwargs):
                    data = (
                        result.data[0]
                        if hasattr(result, "data") and len(result.data) > 0
                        else {}
                    )
                    response = [
                        {
                            "role": "assistant",
                            "content": {
                                "url": data.url if hasattr(data, "url") else "",
                                "revised_prompt": (
                                    data.revised_prompt
                                    if hasattr(data, "revised_prompt")
                                    else ""
                                ),
                            },
                        }
                    ]
                    set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def async_images_generate(original_method, version, tracer):
    """
    Wrap the `generate` method of the `Images` class to trace it.
    """

    async def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["OPENAI"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_GENERATION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_GENERATION"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                set_span_attribute(span, field, value)
            try:
                # Attempt to call the original method
                result = await wrapped(*args, **kwargs)
                if not is_streaming(kwargs):
                    data = (
                        result.data[0]
                        if hasattr(result, "data") and len(result.data) > 0
                        else {}
                    )
                    response = [
                        {
                            "role": "assistant",
                            "content": {
                                "url": data.url if hasattr(data, "url") else "",
                                "revised_prompt": (
                                    data.revised_prompt
                                    if hasattr(data, "revised_prompt")
                                    else ""
                                ),
                            },
                        }
                    ]
                    set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def images_edit(original_method, version, tracer):
    """
    Wrap the `edit` method of the `Images` class to trace it.
    """

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["OPENAI"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_EDIT"]["ENDPOINT"],
            SpanAttributes.LLM_RESPONSE_FORMAT: kwargs.get("response_format"),
            SpanAttributes.LLM_IMAGE_SIZE: kwargs.get("size"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_EDIT"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)

                response = []
                # Parse each image object
                for each_data in result.data:
                    response.append(
                        {
                            "role": "assistant",
                            "content": {
                                "url": each_data.url,
                                "revised_prompt": each_data.revised_prompt,
                                "base64": each_data.b64_json,
                            },
                        }
                    )

                set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


class StreamWrapper:
    span: Span

    def __init__(
        self, stream, span, prompt_tokens, function_call=False, tool_calls=False
    ):
        self.stream = stream
        self.span = span
        self.prompt_tokens = prompt_tokens
        self.function_call = function_call
        self.tool_calls = tool_calls
        self.result_content = []
        self.completion_tokens = 0
        self._span_started = False
        self.setup()

    def setup(self):
        if not self._span_started:
            self.span.add_event(Event.STREAM_START.value)
            self._span_started = True

    def cleanup(self):
        if self._span_started:
            self.span.add_event(Event.STREAM_END.value)
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                self.prompt_tokens,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                self.completion_tokens,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                self.prompt_tokens + self.completion_tokens,
            )
            set_event_completion(
                self.span,
                [
                    {
                        "role": "assistant",
                        "content": "".join(self.result_content),
                    }
                ],
            )

            self.span.set_status(StatusCode.OK)
            self.span.end()
            self._span_started = False

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    async def __aenter__(self):
        self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            chunk = next(self.stream)
            self.process_chunk(chunk)
            return chunk
        except StopIteration:
            self.cleanup()
            raise

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            chunk = await self.stream.__anext__()
            self.process_chunk(chunk)
            return chunk
        except StopAsyncIteration:
            self.cleanup()
            raise StopAsyncIteration

    def process_chunk(self, chunk):
        if hasattr(chunk, "model") and chunk.model is not None:
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_RESPONSE_MODEL,
                chunk.model,
            )

        if hasattr(chunk, "choices") and chunk.choices is not None:
            content = []
            if not self.function_call and not self.tool_calls:
                for choice in chunk.choices:
                    if choice.delta and choice.delta.content is not None:
                        token_counts = estimate_tokens(choice.delta.content)
                        self.completion_tokens += token_counts
                        content = [choice.delta.content]
            elif self.function_call:
                for choice in chunk.choices:
                    if (
                        choice.delta
                        and choice.delta.function_call is not None
                        and choice.delta.function_call.arguments is not None
                    ):
                        token_counts = estimate_tokens(
                            choice.delta.function_call.arguments
                        )
                        self.completion_tokens += token_counts
                        content = [choice.delta.function_call.arguments]
            elif self.tool_calls:
                for choice in chunk.choices:
                    if choice.delta and choice.delta.tool_calls is not None:
                        toolcalls = choice.delta.tool_calls
                        content = []
                        for tool_call in toolcalls:
                            if (
                                tool_call
                                and tool_call.function is not None
                                and tool_call.function.arguments is not None
                            ):
                                token_counts = estimate_tokens(
                                    tool_call.function.arguments
                                )
                                self.completion_tokens += token_counts
                                content.append(tool_call.function.arguments)
            self.span.add_event(
                Event.STREAM_OUTPUT.value,
                {
                    SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK: (
                        "".join(content)
                        if len(content) > 0 and content[0] is not None
                        else ""
                    )
                },
            )
            if content:
                self.result_content.append(content[0])

        if hasattr(chunk, "text"):
            print("chunk", chunk.text, chunk)
            token_counts = estimate_tokens(chunk.text)
            self.completion_tokens += token_counts
            content = [chunk.text]
            self.span.add_event(
                Event.STREAM_OUTPUT.value,
                {
                    SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK: (
                        "".join(content)
                        if len(content) > 0 and content[0] is not None
                        else ""
                    )
                },
            )
            if content:
                self.result_content.append(content[0])


def chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        llm_prompts = []
        for item in kwargs.get("messages", []):
            tools = get_tool_calls(item)
            if tools is not None:
                tool_calls = []
                for tool_call in tools:
                    tool_call_dict = {
                        "id": tool_call.id if hasattr(tool_call, "id") else "",
                        "type": tool_call.type if hasattr(tool_call, "type") else "",
                    }
                    if hasattr(tool_call, "function"):
                        tool_call_dict["function"] = {
                            "name": (
                                tool_call.function.name
                                if hasattr(tool_call.function, "name")
                                else ""
                            ),
                            "arguments": (
                                tool_call.function.arguments
                                if hasattr(tool_call.function, "arguments")
                                else ""
                            ),
                        }
                    tool_calls.append(tool_call_dict)
                llm_prompts.append(tool_calls)
            else:
                llm_prompts.append(item)

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            APIS["CHAT_COMPLETION"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        )
        _set_input_attributes(span, kwargs, attributes)

        try:
            result = wrapped(*args, **kwargs)
            if is_streaming(kwargs):
                prompt_tokens = 0
                for message in kwargs.get("messages", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(message), kwargs.get("model")
                    )

                if (
                    kwargs.get("functions") is not None
                    and kwargs.get("functions") != NOT_GIVEN
                ):
                    for function in kwargs.get("functions"):
                        prompt_tokens += calculate_prompt_tokens(
                            json.dumps(function), kwargs.get("model")
                        )

                return StreamWrapper(
                    result,
                    span,
                    prompt_tokens,
                    function_call=kwargs.get("functions") is not None,
                    tool_calls=kwargs.get("tools") is not None,
                )
            else:
                _set_response_attributes(span, kwargs, result)
                span.set_status(StatusCode.OK)
                span.end()
                return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def async_chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    async def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        llm_prompts = []
        for item in kwargs.get("messages", []):
            tools = get_tool_calls(item)
            if tools is not None:
                tool_calls = []
                for tool_call in tools:
                    tool_call_dict = {
                        "id": tool_call.id if hasattr(tool_call, "id") else "",
                        "type": tool_call.type if hasattr(tool_call, "type") else "",
                    }
                    if hasattr(tool_call, "function"):
                        tool_call_dict["function"] = {
                            "name": (
                                tool_call.function.name
                                if hasattr(tool_call.function, "name")
                                else ""
                            ),
                            "arguments": (
                                tool_call.function.arguments
                                if hasattr(tool_call.function, "arguments")
                                else ""
                            ),
                        }
                    tool_calls.append(json.dumps(tool_call_dict))
                llm_prompts.append(tool_calls)
            else:
                llm_prompts.append(item)

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            APIS["CHAT_COMPLETION"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        )
        _set_input_attributes(span, kwargs, attributes)

        try:
            result = await wrapped(*args, **kwargs)
            if is_streaming(kwargs):
                prompt_tokens = 0
                for message in kwargs.get("messages", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(message), kwargs.get("model")
                    )

                if (
                    kwargs.get("functions") is not None
                    and kwargs.get("functions") != NOT_GIVEN
                ):
                    for function in kwargs.get("functions"):
                        prompt_tokens += calculate_prompt_tokens(
                            json.dumps(function), kwargs.get("model")
                        )

                return StreamWrapper(
                    result,
                    span,
                    prompt_tokens,
                    function_call=kwargs.get("functions") is not None,
                    tool_calls=kwargs.get("tools") is not None,
                )
            else:
                _set_response_attributes(span, kwargs, result)
                span.set_status(StatusCode.OK)
                span.end()
                return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def embeddings_create(original_method, version, tracer):
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["OPENAI"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DIMENSIONS: kwargs.get("dimensions"),
            **get_extra_attributes(),
        }

        encoding_format = kwargs.get("encoding_format")
        if encoding_format is not None:
            if not isinstance(encoding_format, list):
                encoding_format = [encoding_format]
            span_attributes[SpanAttributes.LLM_REQUEST_ENCODING_FORMATS] = (
                encoding_format
            )

        if kwargs.get("input") is not None:
            span_attributes[SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS] = json.dumps(
                [kwargs.get("input", "")]
            )

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["EMBEDDINGS_CREATE"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            for field, value in attributes.model_dump(by_alias=True).items():
                set_span_attribute(span, field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def async_embeddings_create(original_method, version, tracer):
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """

    async def traced_method(wrapped, instance, args, kwargs):

        service_provider = SERVICE_PROVIDERS["OPENAI"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            SpanAttributes.LLM_PATH: APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DIMENSIONS: kwargs.get("dimensions"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        encoding_format = kwargs.get("encoding_format")
        if encoding_format is not None:
            if not isinstance(encoding_format, list):
                encoding_format = [encoding_format]
            span_attributes[SpanAttributes.LLM_REQUEST_ENCODING_FORMATS] = (
                encoding_format
            )

        if kwargs.get("input") is not None:
            span_attributes[SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS] = json.dumps(
                [kwargs.get("input", "")]
            )

        with tracer.start_as_current_span(
            APIS["EMBEDDINGS_CREATE"]["METHOD"],
            kind=SpanKind.CLIENT.value,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            for field, value in attributes.model_dump(by_alias=True).items():
                set_span_attribute(span, field, value)
            try:
                # Attempt to call the original method
                result = await wrapped(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def extract_content(choice):
    # Check if choice.message exists and has a content attribute
    if (
        hasattr(choice, "message")
        and hasattr(choice.message, "content")
        and choice.message.content is not None
    ):
        return choice.message.content

    # Check if choice.message has tool_calls and extract information accordingly
    elif (
        hasattr(choice, "message")
        and hasattr(choice.message, "tool_calls")
        and choice.message.tool_calls is not None
    ):
        result = [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in choice.message.tool_calls
        ]
        return result

    # Check if choice.message has a function_call and extract information accordingly
    elif (
        hasattr(choice, "message")
        and hasattr(choice.message, "function_call")
        and choice.message.function_call is not None
    ):
        return {
            "name": choice.message.function_call.name,
            "arguments": choice.message.function_call.arguments,
        }

    # Return an empty string if none of the above conditions are met
    else:
        return ""


@silently_fail
def _set_input_attributes(span, kwargs, attributes):

    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)

    if kwargs.get("functions") is not None and kwargs.get("functions") != NOT_GIVEN:
        tools = []
        for function in kwargs.get("functions"):
            tools.append(json.dumps({"type": "function", "function": function}))

    if kwargs.get("tools") is not None and kwargs.get("tools") != NOT_GIVEN:
        tools.append(json.dumps(kwargs.get("tools")))

    if tools:
        set_span_attribute(span, SpanAttributes.LLM_TOOLS, json.dumps(tools))


@silently_fail
def _set_response_attributes(span, kwargs, result):
    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, result.model)
    if hasattr(result, "choices") and result.choices is not None:
        responses = [
            {
                "role": (
                    choice.message.role
                    if choice.message and choice.message.role
                    else "assistant"
                ),
                "content": extract_content(choice),
                **(
                    {"content_filter_results": choice["content_filter_results"]}
                    if "content_filter_results" in choice
                    else {}
                ),
            }
            for choice in result.choices
        ]
        set_event_completion(span, responses)

    if (
        hasattr(result, "system_fingerprint")
        and result.system_fingerprint is not None
        and result.system_fingerprint != NOT_GIVEN
    ):
        set_span_attribute(
            span,
            SpanAttributes.LLM_SYSTEM_FINGERPRINT,
            result.system_fingerprint,
        )
    # Get the usage
    if hasattr(result, "usage") and result.usage is not None:
        usage = result.usage
        if usage is not None:
            set_span_attribute(
                span,
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                result.usage.prompt_tokens,
            )
            set_span_attribute(
                span,
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                result.usage.completion_tokens,
            )
            set_span_attribute(
                span,
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                result.usage.total_tokens,
            )
