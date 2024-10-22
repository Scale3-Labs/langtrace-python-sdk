import json
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union
from langtrace.trace_attributes import (
    LLMSpanAttributes,
    SpanAttributes,
)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Tracer, Span
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.common import (
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.litellm import APIS
from langtrace_python_sdk.utils.llm import (
    calculate_prompt_tokens,
    get_base_url,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_span_name,
    get_tool_calls,
    is_streaming,
    set_event_completion,
    StreamWrapper,
    set_span_attributes,
)
from langtrace_python_sdk.types import NOT_GIVEN

from langtrace_python_sdk.instrumentation.openai.types import (
    ImagesGenerateKwargs,
    ChatCompletionsCreateKwargs,
    EmbeddingsCreateKwargs,
    ImagesEditKwargs,
    ResultType,
    ContentItem,
)


def filter_valid_attributes(attributes):
    """Filter attributes where value is not None, not an empty string."""
    return {
        key: value
        for key, value in attributes.items()
        if value is not None and value != ""
    }


def images_generate(version: str, tracer: Tracer) -> Callable:
    """
    Wrap the `generate` method of the `Images` class to trace it.
    """

    def traced_method(
        wrapped: Callable, instance: Any, args: List[Any], kwargs: ImagesGenerateKwargs
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["LITELLM"]
        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_generate"),
            SpanAttributes.LLM_URL: "not available",
            SpanAttributes.LLM_PATH: APIS["IMAGES_GENERATION"]["ENDPOINT"],
            **get_extra_attributes(),  # type: ignore
        }

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

        with tracer.start_as_current_span(
            name=get_span_name(APIS["IMAGES_GENERATION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                if not is_streaming(kwargs):
                    data: Optional[ContentItem] = (
                        result.data[0]
                        if hasattr(result, "data") and len(result.data) > 0
                        else None
                    )
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
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def async_images_generate(version: str, tracer: Tracer) -> Callable:
    """
    Wrap the `generate` method of the `Images` class to trace it.
    """

    async def traced_method(
        wrapped: Callable, instance: Any, args: List[Any], kwargs: ImagesGenerateKwargs
    ) -> Awaitable[Any]:
        service_provider = SERVICE_PROVIDERS["LITELLM"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_generate"),
            SpanAttributes.LLM_URL: "not available",
            SpanAttributes.LLM_PATH: APIS["IMAGES_GENERATION"]["ENDPOINT"],
            **get_extra_attributes(),  # type: ignore
        }

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

        with tracer.start_as_current_span(
            name=get_span_name(APIS["IMAGES_GENERATION"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                # Attempt to call the original method
                result = await wrapped(*args, **kwargs)
                if not is_streaming(kwargs):
                    data: Optional[ContentItem] = (
                        result.data[0]
                        if hasattr(result, "data") and len(result.data) > 0
                        else None
                    )
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
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def images_edit(version: str, tracer: Tracer) -> Callable:
    """
    Wrap the `edit` method of the `Images` class to trace it.
    """

    def traced_method(
        wrapped: Callable, instance: Any, args: List[Any], kwargs: ImagesEditKwargs
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["LITELLM"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="images_edit"),
            SpanAttributes.LLM_URL: "not available",
            SpanAttributes.LLM_PATH: APIS["IMAGES_EDIT"]["ENDPOINT"],
            SpanAttributes.LLM_RESPONSE_FORMAT: kwargs.get("response_format"),
            SpanAttributes.LLM_IMAGE_SIZE: kwargs.get("size"),
            **get_extra_attributes(),  # type: ignore
        }

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

        with tracer.start_as_current_span(
            name=APIS["IMAGES_EDIT"]["METHOD"],
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
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


def chat_completions_create(version: str, tracer: Tracer) -> Callable:
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: ChatCompletionsCreateKwargs,
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["LITELLM"]
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        elif "groq" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["GROQ"]
        elif "x.ai" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["XAI"]
        llm_prompts = []
        for item in kwargs.get("messages", []):
            tools = get_tool_calls(item)
            if tools is not None:
                tool_calls = []
                for tool_call in tools:
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
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            SpanAttributes.LLM_URL: "not available",
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),  # type: ignore
        }

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_COMPLETION"]["METHOD"]),
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
                functions = kwargs.get("functions")
                if functions is not None and functions != NOT_GIVEN:
                    for function in functions:
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


def async_chat_completions_create(version: str, tracer: Tracer) -> Callable:
    """Wrap the `create` method of the `ChatCompletion` class to trace it."""

    async def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: ChatCompletionsCreateKwargs,
    ) -> Awaitable[Any]:
        service_provider = SERVICE_PROVIDERS["LITELLM"]
        if "perplexity" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["PPLX"]
        elif "azure" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["AZURE"]
        elif "x.ai" in get_base_url(instance):
            service_provider = SERVICE_PROVIDERS["XAI"]
        llm_prompts = []
        for item in kwargs.get("messages", []):
            tools = get_tool_calls(item)
            if tools is not None:
                tool_calls = []
                for tool_call in tools:
                    tool_call_dict = {
                        "id": getattr(tool_call, "id", ""),
                        "type": getattr(tool_call, "type", ""),
                    }
                    if hasattr(tool_call, "function"):
                        tool_call_dict["function"] = {
                            "name": getattr(tool_call.function, "name", ""),
                            "arguments": getattr(tool_call.function, "arguments", ""),
                        }
                    tool_calls.append(json.dumps(tool_call_dict))
                llm_prompts.append(tool_calls)
            else:
                llm_prompts.append(item)

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            SpanAttributes.LLM_URL: "not available",
            SpanAttributes.LLM_PATH: APIS["CHAT_COMPLETION"]["ENDPOINT"],
            **get_extra_attributes(),  # type: ignore
        }

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

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
                        json.dumps((str(message))), kwargs.get("model")
                    )

                functions = kwargs.get("functions")
                if functions is not None and functions != NOT_GIVEN:
                    for function in functions:
                        prompt_tokens += calculate_prompt_tokens(
                            json.dumps(function), kwargs.get("model")
                        )

                return StreamWrapper(
                    result,
                    span,
                    prompt_tokens,
                    function_call=kwargs.get("functions") is not None,
                    tool_calls=kwargs.get("tools") is not None,
                )  # type: ignore
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


def embeddings_create(version: str, tracer: Tracer) -> Callable:
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """

    def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: EmbeddingsCreateKwargs,
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["LITELLM"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            SpanAttributes.LLM_URL: "not available",
            SpanAttributes.LLM_PATH: APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DIMENSIONS: kwargs.get("dimensions"),
            **get_extra_attributes(),  # type: ignore
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

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

        with tracer.start_as_current_span(
            name=get_span_name(APIS["EMBEDDINGS_CREATE"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            set_span_attributes(span, attributes)
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


def async_embeddings_create(version: str, tracer: Tracer) -> Callable:
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """

    async def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: EmbeddingsCreateKwargs,
    ) -> Awaitable[Any]:

        service_provider = SERVICE_PROVIDERS["LITELLM"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            SpanAttributes.LLM_PATH: APIS["EMBEDDINGS_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DIMENSIONS: kwargs.get("dimensions"),
            **get_extra_attributes(),  # type: ignore
        }

        attributes = LLMSpanAttributes(**filter_valid_attributes(span_attributes))

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
            name=get_span_name(APIS["EMBEDDINGS_CREATE"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            set_span_attributes(span, attributes)
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


def extract_content(choice: Any) -> Union[str, List[Dict[str, Any]], Dict[str, Any]]:
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
def _set_input_attributes(
    span: Span, kwargs: ChatCompletionsCreateKwargs, attributes: LLMSpanAttributes
) -> None:
    tools = []
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)
    functions = kwargs.get("functions")
    if functions is not None and functions != NOT_GIVEN:
        for function in functions:
            tools.append(json.dumps({"type": "function", "function": function}))

    if kwargs.get("tools") is not None and kwargs.get("tools") != NOT_GIVEN:
        tools.append(json.dumps(kwargs.get("tools")))

    if tools:
        set_span_attribute(span, SpanAttributes.LLM_TOOLS, json.dumps(tools))


@silently_fail
def _set_response_attributes(span: Span, result: ResultType) -> None:
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
                    {"content_filter_results": choice.content_filter_results}
                    if hasattr(choice, "content_filter_results")
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
