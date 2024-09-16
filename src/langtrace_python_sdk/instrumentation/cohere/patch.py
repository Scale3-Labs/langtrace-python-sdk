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

from langtrace_python_sdk.utils.llm import (
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_extra_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    set_usage_attributes,
)
from langtrace.trace_attributes import Event, LLMSpanAttributes
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.misc import datetime_encoder
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from langtrace_python_sdk.constants.instrumentation.common import (
    SERVICE_PROVIDERS,
)
from langtrace.trace_attributes import SpanAttributes


def rerank(original_method, version, tracer):
    """Wrap the `rerank` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, operation_name="rerank"),
            **get_llm_url(instance),
            SpanAttributes.LLM_REQUEST_MODEL: kwargs.get("model") or "command-r-plus",
            SpanAttributes.LLM_URL: APIS["RERANK"]["URL"],
            SpanAttributes.LLM_PATH: APIS["RERANK"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DOCUMENTS: json.dumps(
                kwargs.get("documents"), cls=datetime_encoder
            ),
            SpanAttributes.LLM_COHERE_RERANK_QUERY: kwargs.get("query"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["RERANK"]["METHOD"]), kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)

            if hasattr(result, "results") and result.results is not None:
                results = []
                for _, doc in enumerate(result.results):
                    results.append(doc.json())
                span.set_attribute(
                    SpanAttributes.LLM_COHERE_RERANK_RESULTS, json.dumps(results)
                )

            if (hasattr(result, "response_id")) and (result.response_id is not None):
                span.set_attribute(SpanAttributes.LLM_RESPONSE_ID, result.response_id)

            if hasattr(result, "meta") and result.meta is not None:
                if (
                    hasattr(result.meta, "billed_units")
                    and result.meta.billed_units is not None
                ):
                    usage = result.meta.billed_units
                    if usage is not None:
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                            usage.input_tokens or 0,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                            usage.output_tokens or 0,
                        )

                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                            (usage.input_tokens or 0) + (usage.output_tokens or 0),
                        )

                        span.set_attribute(
                            "search_units",
                            usage.search_units or 0,
                        )

            span.set_status(StatusCode.OK)
            span.end()
            return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def embed(original_method, version, tracer):
    """Wrap the `embed` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            **get_llm_url(instance),
            SpanAttributes.LLM_URL: APIS["EMBED"]["URL"],
            SpanAttributes.LLM_PATH: APIS["EMBED"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS: json.dumps(
                kwargs.get("texts")
            ),
            SpanAttributes.LLM_REQUEST_EMBEDDING_DATASET_ID: kwargs.get("dataset_id"),
            SpanAttributes.LLM_REQUEST_EMBEDDING_INPUT_TYPE: kwargs.get("input_type"),
            SpanAttributes.LLM_REQUEST_EMBEDDING_JOB_NAME: kwargs.get("name"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["EMBED"]["METHOD"]),
            kind=SpanKind.CLIENT,
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)

            if hasattr(result, "meta") and result.meta is not None:
                if (
                    hasattr(result.meta, "billed_units")
                    and result.meta.billed_units is not None
                ):
                    usage = result.meta.billed_units
                    set_usage_attributes(span, dict(usage))

            span.set_status(StatusCode.OK)
            span.end()
            return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def chat_create(original_method, version, tracer):
    """Wrap the `chat_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        message = kwargs.get("message", "")
        prompts = [{"role": "user", "content": message}]
        system_prompts = []
        history = []
        preamble = kwargs.get("preamble")
        if preamble:
            system_prompts = [{"role": "system", "content": preamble}]

        chat_history = kwargs.get("chat_history")
        if chat_history:
            history = [
                {
                    "role": (
                        item.get("role") if item.get("role") is not None else "user"
                    ),
                    "content": (
                        item.get("message") if item.get("message") is not None else ""
                    ),
                }
                for item in chat_history
            ]
        if len(history) > 0:
            prompts = history + prompts
        if len(system_prompts) > 0:
            prompts = system_prompts + prompts

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_REQUEST_MODEL: kwargs.get("model") or "command-r-plus",
            SpanAttributes.LLM_URL: APIS["CHAT_CREATE"]["URL"],
            SpanAttributes.LLM_PATH: APIS["CHAT_CREATE"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("max_input_tokens") is not None:
            attributes.llm_max_input_tokens = str(kwargs.get("max_input_tokens"))

        if kwargs.get("conversation_id") is not None:
            attributes.conversation_id = kwargs.get("conversation_id")

        if kwargs.get("connectors") is not None:
            # stringify the list of objects
            attributes.llm_connectors = json.dumps(kwargs.get("connectors"))
        if kwargs.get("tools") is not None:
            # stringify the list of objects
            attributes.llm_tools = json.dumps(kwargs.get("tools"))
        if kwargs.get("tool_results") is not None:
            # stringify the list of objects
            attributes.llm_tool_results = json.dumps(kwargs.get("tool_results"))

        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_CREATE"]["METHOD"]), kind=SpanKind.CLIENT
        )

        # Set the attributes on the span
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)

            # Set the response attributes
            if (hasattr(result, "generation_id")) and (
                result.generation_id is not None
            ):
                span.set_attribute(
                    SpanAttributes.LLM_GENERATION_ID, result.generation_id
                )
            if (hasattr(result, "response_id")) and (result.response_id is not None):
                span.set_attribute(SpanAttributes.LLM_RESPONSE_ID, result.response_id)
            if (hasattr(result, "is_search_required")) and (
                result.is_search_required is not None
            ):
                span.set_attribute(
                    SpanAttributes.LLM_REQUEST_SEARCH_REQUIRED,
                    result.is_search_required,
                )

            if kwargs.get("stream") is False or kwargs.get("stream") is None:
                if (
                    hasattr(result, "text")
                    and result.text is not None
                    and result.text != ""
                ):
                    if (
                        hasattr(result, "chat_history")
                        and result.chat_history is not None
                    ):
                        responses = [
                            {
                                "role": (
                                    item.role
                                    if hasattr(item, "role") and item.role is not None
                                    else "user"
                                ),
                                "content": (
                                    item.message
                                    if hasattr(item, "message")
                                    and item.message is not None
                                    else ""
                                ),
                            }
                            for item in result.chat_history
                        ]
                        set_event_completion(span, responses)

                    else:
                        responses = [{"role": "CHATBOT", "content": result.text}]
                        set_event_completion(span, responses)

                elif hasattr(result, "tool_calls") and result.tool_calls is not None:
                    tool_calls = []
                    for tool_call in result.tool_calls:
                        tool_calls.append(tool_call.json())
                    span.set_attribute(
                        SpanAttributes.LLM_TOOL_RESULTS, json.dumps(tool_calls)
                    )

                # Get the usage
                if hasattr(result, "meta") and result.meta is not None:
                    if (
                        hasattr(result.meta, "billed_units")
                        and result.meta.billed_units is not None
                    ):
                        usage = result.meta.billed_units
                        if usage is not None:
                            span.set_attribute(
                                SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                                usage.input_tokens or 0,
                            )
                            span.set_attribute(
                                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                                usage.output_tokens or 0,
                            )

                            span.set_attribute(
                                SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                                (usage.input_tokens or 0) + (usage.output_tokens or 0),
                            )

                            span.set_attribute(
                                "search_units",
                                usage.search_units or 0,
                            )
                span.set_status(StatusCode.OK)
                span.end()
                return result
            else:
                # For older version, stream was passed as a parameter
                return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def chat_stream(original_method, version, tracer):
    """Wrap the `messages_stream` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        message = kwargs.get("message", "")
        prompts = [{"role": "user", "content": message}]
        system_prompts = []
        history = []
        preamble = kwargs.get("preamble")
        if preamble:
            system_prompts = [{"role": "system", "content": preamble}]

        chat_history = kwargs.get("chat_history")
        if chat_history:
            history = [
                {
                    "role": (
                        item.get("role") if item.get("role") is not None else "user"
                    ),
                    "content": (
                        item.get("message") if item.get("message") is not None else ""
                    ),
                }
                for item in chat_history
            ]
        prompts = system_prompts + history + prompts

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_REQUEST_MODEL: kwargs.get("model") or "command-r-plus",
            SpanAttributes.LLM_IS_STREAMING: True,
            SpanAttributes.LLM_URL: APIS["CHAT_STREAM"]["URL"],
            SpanAttributes.LLM_PATH: APIS["CHAT_STREAM"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        if kwargs.get("max_input_tokens") is not None:
            attributes.llm_max_input_tokens = str(kwargs.get("max_input_tokens"))

        if kwargs.get("connectors") is not None:
            # stringify the list of objects
            attributes.llm_connectors = json.dumps(kwargs.get("connectors"))
        if kwargs.get("tools") is not None:
            # stringify the list of objects
            attributes.llm_tools = json.dumps(kwargs.get("tools"))
        if kwargs.get("tool_results") is not None:
            # stringify the list of objects
            attributes.llm_tool_results = json.dumps(kwargs.get("tool_results"))

        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_STREAM"]["METHOD"]), kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            try:
                for event in result:
                    if (
                        hasattr(event, "finish_reason")
                        and event.finish_reason == "COMPLETE"
                    ):
                        response = event.response
                        if (hasattr(response, "generation_id")) and (
                            response.generation_id is not None
                        ):
                            span.set_attribute(
                                SpanAttributes.LLM_GENERATION_ID,
                                response.generation_id,
                            )
                        if (hasattr(response, "response_id")) and (
                            response.response_id is not None
                        ):
                            span.set_attribute(
                                SpanAttributes.LLM_RESPONSE_ID,
                                response.response_id,
                            )
                        if (hasattr(response, "is_search_required")) and (
                            response.is_search_required is not None
                        ):
                            span.set_attribute(
                                SpanAttributes.LLM_REQUEST_SEARCH_REQUIRED,
                                response.is_search_required,
                            )

                        # Set the response attributes
                        if hasattr(response, "text") and response.text is not None:
                            if (
                                hasattr(response, "chat_history")
                                and response.chat_history is not None
                            ):
                                responses = [
                                    {
                                        "role": (
                                            item.role
                                            if hasattr(item, "role")
                                            and item.role is not None
                                            else "user"
                                        ),
                                        "content": (
                                            item.message
                                            if hasattr(item, "message")
                                            and item.message is not None
                                            else ""
                                        ),
                                    }
                                    for item in response.chat_history
                                ]
                                set_event_completion(span, responses)

                            else:
                                responses = [
                                    {"role": "CHATBOT", "content": response.text}
                                ]
                                set_event_completion(span, responses)

                        # Get the usage
                        if hasattr(response, "meta") and response.meta is not None:
                            if (
                                hasattr(response.meta, "billed_units")
                                and response.meta.billed_units is not None
                            ):
                                usage = response.meta.billed_units
                                if usage is not None:
                                    span.set_attribute(
                                        SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                                        usage.input_tokens or 0,
                                    )
                                    span.set_attribute(
                                        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                                        usage.output_tokens or 0,
                                    )

                                    span.set_attribute(
                                        SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                                        (usage.input_tokens or 0)
                                        + (usage.output_tokens or 0),
                                    )
                                    if usage.search_units is not None:
                                        span.set_attribute(
                                            "search_units",
                                            usage.search_units or 0,
                                        )

                    yield event
            finally:
                span.set_status(StatusCode.OK)
                span.end()

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method
