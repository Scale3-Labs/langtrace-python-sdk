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

from importlib_metadata import version as v
from langtrace.trace_attributes import Event, LLMSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from langtrace_python_sdk.utils.llm import calculate_prompt_tokens, estimate_tokens


def images_generate(original_method, version, tracer):
    """
    Wrap the `generate` method of the `Images` class to trace it.
    """

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["IMAGES_GENERATION"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.stream": kwargs.get("stream"),
            "llm.prompts": json.dumps(
                [{"role": "user", "content": kwargs.get("prompt", [])}]
            ),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_GENERATION"]["METHOD"], kind=SpanKind.CLIENT
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                if kwargs.get("stream") is False or kwargs.get("stream") is None:
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
                    span.set_attribute("llm.responses", json.dumps(response))

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
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["IMAGES_GENERATION"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.stream": kwargs.get("stream"),
            "llm.prompts": json.dumps(
                [{"role": "user", "content": kwargs.get("prompt", [])}]
            ),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_GENERATION"]["METHOD"], kind=SpanKind.CLIENT
        ) as span:
            items = attributes.model_dump(by_alias=True).items()
            for field, value in items:
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = await wrapped(*args, **kwargs)
                if kwargs.get("stream") is False or kwargs.get("stream") is None:
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
                    span.set_attribute("llm.responses", json.dumps(response))

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
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["IMAGES_EDIT"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.response_format": kwargs.get("response_format"),
            "llm.image.size": kwargs.get("size"),
            "llm.prompts": json.dumps(
                [
                    {
                        "role": kwargs.get("user", "user"),
                        "content": kwargs.get("prompt", []),
                    }
                ]
            ),
            "llm.top_k": kwargs.get("n"),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_EDIT"]["METHOD"], kind=SpanKind.CLIENT
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

                span.add_event(
                    name="response",
                    attributes={"llm.responses": json.dumps(response)},
                )

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


def chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        # If base url contains perplexity or azure, set the service provider accordingly
        if "perplexity" in base_url:
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in base_url:
            service_provider = SERVICE_PROVIDERS["AZURE"]

        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

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
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.prompts": json.dumps(llm_prompts),
            "llm.stream": kwargs.get("stream"),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        tools = []
        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("top_p") is not None:
            attributes.llm_top_p = kwargs.get("top_p")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")
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
            APIS["CHAT_COMPLETION"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if kwargs.get("stream") is False or kwargs.get("stream") is None:
                span.set_attribute("llm.model", result.model)
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
                    span.set_attribute("llm.responses", json.dumps(responses))
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
                            "input_tokens": result.usage.prompt_tokens,
                            "output_tokens": usage.completion_tokens,
                            "total_tokens": usage.total_tokens,
                        }
                        span.set_attribute("llm.token.counts", json.dumps(usage_dict))
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
                span.add_event(
                    Event.STREAM_OUTPUT.value,
                    {
                        "response": (
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
            span.set_attribute(
                "llm.token.counts",
                json.dumps(
                    {
                        "input_tokens": prompt_tokens,
                        "output_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    }
                ),
            )
            span.set_attribute(
                "llm.responses",
                json.dumps(
                    [
                        {
                            "role": "assistant",
                            "content": "".join(result_content),
                        }
                    ]
                ),
            )
            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
    return traced_method


def async_chat_completions_create(original_method, version, tracer):
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    async def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )
        service_provider = SERVICE_PROVIDERS["OPENAI"]
        # If base url contains perplexity or azure, set the service provider accordingly
        if "perplexity" in base_url:
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in base_url:
            service_provider = SERVICE_PROVIDERS["AZURE"]

        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

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
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["CHAT_COMPLETION"]["ENDPOINT"],
            "llm.prompts": json.dumps(llm_prompts),
            "llm.stream": kwargs.get("stream"),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        tools = []
        if kwargs.get("temperature") is not None:
            attributes.llm_temperature = kwargs.get("temperature")
        if kwargs.get("top_p") is not None:
            attributes.llm_top_p = kwargs.get("top_p")
        if kwargs.get("user") is not None:
            attributes.llm_user = kwargs.get("user")
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
            APIS["CHAT_COMPLETION"]["METHOD"], kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = await wrapped(*args, **kwargs)
            if kwargs.get("stream") is False or kwargs.get("stream") is None:
                span.set_attribute("llm.model", result.model)
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
                    span.set_attribute("llm.responses", json.dumps(responses))
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
                            "input_tokens": result.usage.prompt_tokens,
                            "output_tokens": usage.completion_tokens,
                            "total_tokens": usage.total_tokens,
                        }
                        span.set_attribute("llm.token.counts", json.dumps(usage_dict))
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
            content = []
            async for chunk in result:
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
                                        content = content + [
                                            tool_call.function.arguments
                                        ]
                                    else:
                                        content = content + []
                else:
                    content = []
                span.add_event(
                    Event.STREAM_OUTPUT.value,
                    {
                        "response": (
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
            span.set_attribute(
                "llm.token.counts",
                json.dumps(
                    {
                        "input_tokens": prompt_tokens,
                        "output_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    }
                ),
            )
            span.set_attribute(
                "llm.responses",
                json.dumps(
                    [
                        {
                            "role": "assistant",
                            "content": "".join(result_content),
                        }
                    ]
                ),
            )
            span.set_status(StatusCode.OK)
            span.end()

    # return the wrapped method
    return traced_method


def embeddings_create(original_method, version, tracer):
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """

    def traced_method(wrapped, instance, args, kwargs):
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )

        service_provider = SERVICE_PROVIDERS["OPENAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": "",
            "llm.embedding_inputs": json.dumps([kwargs.get("input", "")]),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        if kwargs.get("encoding_format") is not None:
            span_attributes["llm.encoding.formats"] = json.dumps(
                [kwargs.get("encoding_format")]
            )

        attributes = LLMSpanAttributes(**span_attributes)
        kwargs.get("encoding_format")

        if kwargs.get("dimensions") is not None:
            attributes["llm.dimensions"] = kwargs.get("dimensions")
        if kwargs.get("user") is not None:
            attributes["llm.user"] = kwargs.get("user")

        with tracer.start_as_current_span(
            APIS["EMBEDDINGS_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        ) as span:

            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
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
        base_url = (
            str(instance._client._base_url)
            if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
            else ""
        )

        service_provider = SERVICE_PROVIDERS["OPENAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "llm",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "url.full": base_url,
            "llm.api": APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            "llm.model": kwargs.get("model"),
            "llm.prompts": json.dumps(
                [{"role": "user", "content": kwargs.get("input", "")}]
            ),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)
        kwargs.get("encoding_format")

        if kwargs.get("encoding_format") is not None:
            attributes.llm_encoding_format = kwargs.get("encoding_format")
        if kwargs.get("dimensions") is not None:
            attributes["llm.dimensions"] = kwargs.get("dimensions")
        if kwargs.get("user") is not None:
            attributes["llm.user"] = kwargs.get("user")

        with tracer.start_as_current_span(
            APIS["EMBEDDINGS_CREATE"]["METHOD"], kind=SpanKind.CLIENT
        ) as span:

            async for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
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
