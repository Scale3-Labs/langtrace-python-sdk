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
from opentelemetry import baggage, trace
from opentelemetry.trace.propagation import set_span_in_context
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.utils.llm import (
    get_base_url,
    get_extra_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_langtrace_attributes,
    get_span_name,
    set_event_completion,
    set_usage_attributes,
)
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.groq import APIS
from langtrace_python_sdk.utils.llm import calculate_prompt_tokens, estimate_tokens
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace.trace_attributes import SpanAttributes


def chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["GROQ"]
        # If base url contains perplexity or azure, set the service provider accordingly
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        elif "x.ai" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["XAI"]

        # handle tool calls in the kwargs
        llm_prompts = []
        for item in kwargs.get("messages", []):
            if hasattr(item, "tool_calls") and item.tool_calls is not None:
                tool_calls = []
                for tool_call in item.tool_calls:
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
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        tools = []
        if kwargs.get("functions") is not None:
            for function in kwargs.get("functions"):
                tools.append(json.dumps({"type": "function", "function": function}))
        if kwargs.get("tools") is not None:
            tools.append(json.dumps(kwargs.get("tools")))
        if len(tools) > 0:
            attributes.llm_tools = json.dumps(tools)

        # TODO(Karthik): Gotta figure out how to handle streaming with context
        # with tracer.start_as_current_span(APIS["CHAT_COMPLETION"]["METHOD"],
        #                                   kind=SpanKind.CLIENT) as span:
        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_COMPLETION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if kwargs.get("stream") is False or kwargs.get("stream") is None:
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, result.model
                )
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
                                {
                                    "content_filter_results": choice[
                                        "content_filter_results"
                                    ]
                                }
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
                ):
                    set_span_attribute(
                        span,
                        SpanAttributes.LLM_SYSTEM_FINGERPRINT,
                        result.system_fingerprint,
                    )

                # Get the usage
                if hasattr(result, "usage") and result.usage is not None:
                    usage = result.usage
                    set_usage_attributes(span, dict(usage))

                span.set_status(Status(StatusCode.OK))
                span.end()
                return result
            else:
                # iterate over kwargs.get("messages", {}) and calculate the prompt tokens
                prompt_tokens = 0
                for message in kwargs.get("messages", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(message), kwargs.get("model")
                    )

                # iterate over kwargs.get("functions") and calculate the prompt tokens
                if kwargs.get("functions") is not None:
                    for function in kwargs.get("functions"):
                        prompt_tokens += calculate_prompt_tokens(
                            json.dumps(function), kwargs.get("model")
                        )

                return handle_streaming_response(
                    result,
                    span,
                    prompt_tokens,
                    function_call=kwargs.get("functions") is not None,
                    tool_calls=kwargs.get("tools") is not None,
                )

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    def handle_streaming_response(
        result, span, prompt_tokens, function_call=False, tool_calls=False
    ):
        """Process and yield streaming response chunks."""
        result_content = []
        span.add_event(Event.STREAM_START.value)
        completion_tokens = 0
        try:
            for chunk in result:
                if hasattr(chunk, "model") and chunk.model is not None:
                    span.set_attribute("llm.model", chunk.model)
                if hasattr(chunk, "choices") and chunk.choices is not None:
                    if not function_call and not tool_calls:
                        for choice in chunk.choices:
                            if choice.delta and choice.delta.content is not None:
                                token_counts = estimate_tokens(choice.delta.content)
                                completion_tokens += token_counts
                                content = [choice.delta.content]
                    elif function_call:
                        for choice in chunk.choices:
                            if (
                                choice.delta
                                and choice.delta.function_call is not None
                                and choice.delta.function_call.arguments is not None
                            ):
                                token_counts = estimate_tokens(
                                    choice.delta.function_call.arguments
                                )
                                completion_tokens += token_counts
                                content = [choice.delta.function_call.arguments]
                    elif tool_calls:
                        for choice in chunk.choices:
                            tool_call = ""
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
                                        completion_tokens += token_counts
                                        content = content + [
                                            tool_call.function.arguments
                                        ]
                                    else:
                                        content = content + []
                else:
                    content = []

                result_content.append(content[0] if len(content) > 0 else "")
                yield chunk
        finally:
            # Finalize span after processing all chunks
            span.add_event(Event.STREAM_END.value)
            set_usage_attributes(
                span,
                {"input_tokens": prompt_tokens, "output_tokens": completion_tokens},
            )
            set_event_completion(
                span, [{"role": "assistant", "content": "".join(result_content)}]
            )

            span.set_status(Status(StatusCode.OK))
            span.end()

    # return the wrapped method
    return traced_method


def async_chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    async def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["GROQ"]
        # If base url contains perplexity or azure, set the service provider accordingly
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        elif "x.ai" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["XAI"]

        # handle tool calls in the kwargs
        llm_prompts = []
        for item in kwargs.get("messages", []):
            if hasattr(item, "tool_calls") and item.tool_calls is not None:
                tool_calls = []
                for tool_call in item.tool_calls:
                    tool_call_dict = {
                        "id": getattr(tool_call, "id", ""),
                        "type": getattr(tool_call, "type", ""),
                    }
                    if hasattr(tool_call, "function"):
                        tool_call_dict["function"] = {
                            "name": getattr(tool_call.function, "name", ""),
                            "arguments": getattr(tool_call.function, "arguments", ""),
                        }
                    tool_calls.append(tool_call_dict)
                llm_prompts.append(tool_calls)
            else:
                llm_prompts.append(item)

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        tools = []

        if kwargs.get("functions") is not None:
            for function in kwargs.get("functions"):
                tools.append(json.dumps({"type": "function", "function": function}))
        if kwargs.get("tools") is not None:
            tools.append(json.dumps(kwargs.get("tools")))
        if len(tools) > 0:
            attributes.llm_tools = json.dumps(tools)

        # TODO(Karthik): Gotta figure out how to handle streaming with context
        # with tracer.start_as_current_span(APIS["CHAT_COMPLETION"]["METHOD"],
        #                                   kind=SpanKind.CLIENT) as span:
        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_COMPLETION"]["METHOD"]), kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = await wrapped(*args, **kwargs)
            if kwargs.get("stream") is False or kwargs.get("stream") is None:
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, result.model
                )
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
                                {
                                    "content_filter_results": choice[
                                        "content_filter_results"
                                    ]
                                }
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
                        set_usage_attributes(span, dict(usage))

                span.set_status(StatusCode.OK)
                span.end()
                return result
            else:
                # iterate over kwargs.get("messages", {}) and calculate the prompt tokens
                prompt_tokens = 0
                for message in kwargs.get("messages", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(message), kwargs.get("model")
                    )

                # iterate over kwargs.get("functions") and calculate the prompt tokens
                if kwargs.get("functions") is not None:
                    for function in kwargs.get("functions"):
                        prompt_tokens += calculate_prompt_tokens(
                            json.dumps(function), kwargs.get("model")
                        )

                return ahandle_streaming_response(
                    result,
                    span,
                    prompt_tokens,
                    function_call=kwargs.get("functions") is not None,
                    tool_calls=kwargs.get("tools") is not None,
                )

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    async def ahandle_streaming_response(
        result, span, prompt_tokens, function_call=False, tool_calls=False
    ):
        """Process and yield streaming response chunks."""
        result_content = []
        span.add_event(Event.STREAM_START.value)
        completion_tokens = 0
        try:
            async for chunk in result:
                if hasattr(chunk, "model") and chunk.model is not None:
                    set_span_attribute(
                        span, SpanAttributes.LLM_RESPONSE_MODEL, chunk.model
                    )
                    span.set_attribute("llm.model", chunk.model)
                if hasattr(chunk, "choices") and chunk.choices is not None:
                    if not function_call and not tool_calls:
                        for choice in chunk.choices:
                            if choice.delta and choice.delta.content is not None:
                                token_counts = estimate_tokens(choice.delta.content)
                                completion_tokens += token_counts
                                content = [choice.delta.content]
                    elif function_call:
                        for choice in chunk.choices:
                            if (
                                choice.delta
                                and choice.delta.function_call
                                and choice.delta.function_call.arguments is not None
                            ):
                                token_counts = estimate_tokens(
                                    choice.delta.function_call.arguments
                                )
                                completion_tokens += token_counts
                                content = [choice.delta.function_call.arguments]
                    elif tool_calls:
                        for choice in chunk.choices:
                            tool_call = ""
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
                                        completion_tokens += token_counts
                                        content += [tool_call.function.arguments]
                else:
                    content = []
                span.add_event(
                    Event.RESPONSE.value,
                    {
                        SpanAttributes.LLM_COMPLETIONS: (
                            "".join(content)
                            if len(content) > 0 and content[0] is not None
                            else ""
                        )
                    },
                )
                result_content.append(content[0] if len(content) > 0 else "")
                yield chunk
        finally:
            # Finalize span after processing all chunks
            span.add_event(Event.STREAM_END.value)

            set_usage_attributes(
                span,
                {"input_tokens": prompt_tokens, "output_tokens": completion_tokens},
            )

            set_event_completion(
                span,
                [
                    {
                        "role": "assistant",
                        "content": "".join(result_content),
                    }
                ],
            )

            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
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
