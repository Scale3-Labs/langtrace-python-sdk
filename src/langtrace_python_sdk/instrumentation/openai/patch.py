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
from typing import Any, Callable, Dict, List, Union, Tuple
from langtrace_python_sdk.instrumentation.openai.types import(
    ChatCompletionsCreateKwargs,
    EmbeddingsCreateKwargs,
    ImagesEditKwargs,
    ImagesGenerateKwargs
)
from langtrace.trace_attributes import LLMSpanAttributes, SpanAttributes
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.openai import APIS
from langtrace_python_sdk.utils.llm import (
    calculate_prompt_tokens,
    get_base_url,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    is_streaming,
    set_event_completion,
    StreamWrapper,
    set_span_attributes,
)
from openai._types import NOT_GIVEN


def images_generate(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: ImagesGenerateKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]
        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_generate"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_GENERATION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS["IMAGES_GENERATION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                result = wrapped(*args, **kwargs)
                if not is_streaming(kwargs):
                    data = result.data[0] if hasattr(result, "data") and result.data else {}
                    response = [
                        {
                            "role": "assistant",
                            "content": {
                                "url": getattr(data, "url", ""),
                                "revised_prompt": getattr(data, "revised_prompt", ""),
                            },
                        }
                    ]
                    set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def async_images_generate(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    async def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: ImagesGenerateKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]
        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_generate"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_GENERATION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS["IMAGES_GENERATION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                result = await wrapped(*args, **kwargs)
                if not is_streaming(kwargs):
                    data = result.data[0] if hasattr(result, "data") and result.data else {}
                    response = [
                        {
                            "role": "assistant",
                            "content": {
                                "url": getattr(data, "url", ""),
                                "revised_prompt": getattr(data, "revised_prompt", ""),
                            },
                        }
                    ]
                    set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def images_edit(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: ImagesEditKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]
        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_edit"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_EDIT"]["ENDPOINT"],
            SpanAttributes.LLM_RESPONSE_FORMAT: kwargs.get("response_format"),
            SpanAttributes.LLM_IMAGE_SIZE: kwargs.get("size"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=APIS["IMAGES_EDIT"]["METHOD"],
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                result = wrapped(*args, **kwargs)

                response = [
                    {
                        "role": "assistant",
                        "content": {
                            "url": each_data.url,
                            "revised_prompt": each_data.revised_prompt,
                            "base64": each_data.b64_json,
                        },
                    }
                    for each_data in result.data
                ]

                set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def async_images_edit(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    async def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: ImagesEditKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]
        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_edit"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["IMAGES_EDIT"]["ENDPOINT"],
            SpanAttributes.LLM_RESPONSE_FORMAT: kwargs.get("response_format"),
            SpanAttributes.LLM_IMAGE_SIZE: kwargs.get("size"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            APIS["IMAGES_EDIT"]["METHOD"],
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                result = await wrapped(*args, **kwargs)

                response = [
                    {
                        "role": "assistant",
                        "content": {
                            "url": each_data.url,
                            "revised_prompt": each_data.revised_prompt,
                            "base64": each_data.b64_json,
                        },
                    }
                    for each_data in result.data
                ]

                set_event_completion(span, response)

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def chat_completions_create(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: ChatCompletionsCreateKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        elif "groq" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["GROQ"]

        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="chat_completions_create"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_COMPƒLETION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        _set_input_attributes(span, kwargs, attributes)

        try:
            result = wrapped(*args, **kwargs)
            if is_streaming(kwargs):
                prompt_tokens = 0
                for message in kwargs.get("messages", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(str(message)), kwargs.get("model")
                    )

                if (
                    kwargs.get("functions") is not None
                    and kwargs.get("functions") != NOT_GIVEN
                ):
                    for function in kwargs.get("functions") or []:
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
                _set_response_attributes(span, result)
                span.set_status(StatusCode.OK)
                span.end()
                return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def async_chat_completions_create(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    async def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: ChatCompletionsCreateKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        elif "groq" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["GROQ"]

        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="chat_completions_create"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_COMPLETION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        _set_input_attributes(span, kwargs, attributes)

        try:
            result = await wrapped(*args, **kwargs)
            if is_streaming(kwargs):
                prompt_tokens = 0
                for message in kwargs.get("messages", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(str(message)), kwargs.get("model")
                    )

                if (
                    kwargs.get("functions") is not None
                    and kwargs.get("functions") != NOT_GIVEN
                ):
                    for function in kwargs.get("functions") or []:
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
                _set_response_attributes(span, result)
                span.set_status(StatusCode.OK)
                span.end()
                return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def embeddings_create(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: EmbeddingsCreateKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]

        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DIMENSIONS: kwargs.get("dimensions"),
            **get_extra_attributes(),
        }

        encoding_format = kwargs.get("encoding_format")
        if encoding_format is not None:
            if not isinstance(encoding_format, list):
                encoding_format = [encoding_format]
            span_attributes[SpanAttributes.LLM_REQUEST_ENCODING_FORMATS] = encoding_format

        if kwargs.get("input") is not None:
            span_attributes[SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS] = json.dumps(
                [kwargs.get("input", "")]
            )

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS["EMBEDDINGS_CREATE"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            set_span_attributes(span, attributes)
            try:
                result = wrapped(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def async_embeddings_create(
    version: str, tracer: Tracer
) -> Callable[..., Any]:
    async def traced_method(
        wrapped: Callable[..., Any], instance: Any, args: Tuple[Any, ...], kwargs: EmbeddingsCreateKwargs
    ) -> Any:
        service_provider: str = SERVICE_PROVIDERS["OPENAI"]

        span_attributes: Dict[str, Any] = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DIMENSIONS: kwargs.get("dimensions"),
            **get_extra_attributes(),
        }

        encoding_format = kwargs.get("encoding_format")
        if encoding_format is not None:
            if not isinstance(encoding_format, list):
                encoding_format = [encoding_format]
            span_attributes[SpanAttributes.LLM_REQUEST_ENCODING_FORMATS] = encoding_format

        if kwargs.get("input") is not None:
            span_attributes[SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS] = json.dumps(
                [kwargs.get("input", "")]
            )

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS["EMBEDDINGS_CREATE"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            set_span_attributes(span, attributes)
            try:
                result = await wrapped(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method


def extract_content(choice: Any) -> Union[str, List[Dict[str, Any]], Dict[str, str]]:
    # Check if choice.message exists and has a content attribute
    if (
        hasattr(choice, "message")
        and hasattr(choice.message, "content")
        and choice.message.content is not None
    ):
        result: str = choice.message.content
        return result

    # Check if choice.message has tool_calls and extract information accordingly
    elif (
        hasattr(choice, "message")
        and hasattr(choice.message, "tool_calls")
        and choice.message.tool_calls is not None
    ):
        return [
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


@silently_fail # type: ignore
def _set_input_attributes(span: Any, kwargs: ChatCompletionsCreateKwargs, attributes: LLMSpanAttributes) -> None:
    tools: List[str] = []
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)

    if kwargs.get("functions") is not None and kwargs.get("functions") != NOT_GIVEN:
        for function in kwargs.get("functions") or []:
            tools.append(json.dumps({"type": "function", "function": function}))

    if kwargs.get("tools") is not None and kwargs.get("tools") != NOT_GIVEN:
        tools.append(json.dumps(kwargs.get("tools")))

    if tools:
        set_span_attribute(span, SpanAttributes.LLM_TOOLS, json.dumps(tools))


@silently_fail # type: ignore
def _set_response_attributes(span: Any, result: Any) -> None:
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
