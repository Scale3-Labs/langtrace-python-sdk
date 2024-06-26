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

from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace.trace_attributes import SpanAttributes


def rerank(original_method, version, tracer):
    """Wrap the `rerank` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            SpanAttributes.LANGTRACE_SDK_NAME.value: LANGTRACE_SDK_NAME,
            SpanAttributes.LANGTRACE_SERVICE_NAME.value: service_provider,
            SpanAttributes.LANGTRACE_SERVICE_TYPE.value: "llm",
            SpanAttributes.LANGTRACE_SERVICE_VERSION.value: version,
            SpanAttributes.LANGTRACE_VERSION.value: v(LANGTRACE_SDK_NAME),
            SpanAttributes.LLM_URL.value: APIS["RERANK"]["URL"],
            SpanAttributes.LLM_PATH.value: APIS["RERANK"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_MODEL.value: kwargs.get("model"),
            SpanAttributes.LLM_TOP_K.value: kwargs.get("top_n"),
            SpanAttributes.LLM_USER.value: kwargs.get("user"),
            SpanAttributes.LLM_REQUEST_DOCUMENTS.value: json.dumps(
                kwargs.get("documents")
            ),
            SpanAttributes.LLM_COHERE_RERANK_QUERY.value: kwargs.get("query"),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(APIS["RERANK"]["METHOD"], kind=SpanKind.CLIENT)
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
                    SpanAttributes.LLM_COHERE_RERANK_RESULTS.value, json.dumps(results)
                )

            if (hasattr(result, "response_id")) and (result.response_id is not None):
                span.set_attribute(
                    SpanAttributes.LLM_RESPONSE_ID.value, result.response_id
                )

            if hasattr(result, "meta") and result.meta is not None:
                if (
                    hasattr(result.meta, "billed_units")
                    and result.meta.billed_units is not None
                ):
                    usage = result.meta.billed_units
                    if usage is not None:
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value,
                            usage.input_tokens or 0,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value,
                            usage.output_tokens or 0,
                        )

                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
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
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            SpanAttributes.LANGTRACE_SDK_NAME.value: LANGTRACE_SDK_NAME,
            SpanAttributes.LANGTRACE_SERVICE_NAME.value: service_provider,
            SpanAttributes.LANGTRACE_SERVICE_TYPE.value: "llm",
            SpanAttributes.LANGTRACE_SERVICE_VERSION.value: version,
            SpanAttributes.LANGTRACE_VERSION.value: v(LANGTRACE_SDK_NAME),
            SpanAttributes.LLM_URL.value: APIS["EMBED"]["URL"],
            SpanAttributes.LLM_PATH.value: APIS["EMBED"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_MODEL.value: kwargs.get("model"),
            SpanAttributes.LLM_USER.value: kwargs.get("user"),
            SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS.value: json.dumps(
                kwargs.get("texts")
            ),
            SpanAttributes.LLM_REQUEST_EMBEDDING_DATASET_ID.value: kwargs.get(
                "dataset_id"
            ),
            SpanAttributes.LLM_REQUEST_EMBEDDING_INPUT_TYPE.value: kwargs.get(
                "input_type"
            ),
            SpanAttributes.LLM_REQUEST_EMBEDDING_JOB_NAME.value: kwargs.get("name"),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(APIS["EMBED"]["METHOD"], kind=SpanKind.CLIENT)
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
                    if usage is not None:
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value,
                            usage.input_tokens or 0,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value,
                            usage.output_tokens or 0,
                        )

                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
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


def chat_create(original_method, version, tracer):
    """Wrap the `chat_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        message = kwargs.get("message", "")
        prompts = [{"role": "USER", "content": message}]
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
                        item.get("role") if item.get("role") is not None else "USER"
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
        prompts = json.dumps(prompts)

        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            SpanAttributes.LANGTRACE_SDK_NAME.value: LANGTRACE_SDK_NAME,
            SpanAttributes.LANGTRACE_SERVICE_NAME.value: service_provider,
            SpanAttributes.LANGTRACE_SERVICE_TYPE.value: "llm",
            SpanAttributes.LANGTRACE_SERVICE_VERSION.value: version,
            SpanAttributes.LANGTRACE_VERSION.value: v(LANGTRACE_SDK_NAME),
            SpanAttributes.LLM_URL.value: APIS["CHAT_CREATE"]["URL"],
            SpanAttributes.LLM_PATH.value: APIS["CHAT_CREATE"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_MODEL.value: (
                kwargs.get("model", None) or "command-r"
            ),
            SpanAttributes.LLM_IS_STREAMING.value: False,
            SpanAttributes.LLM_PROMPTS.value: prompts,
            SpanAttributes.LLM_REQUEST_TEMPERATURE.value: kwargs.get("temperature"),
            SpanAttributes.LLM_REQUEST_MAX_TOKENS.value: kwargs.get("max_tokens"),
            SpanAttributes.LLM_REQUEST_TOP_P.value: kwargs.get("p"),
            SpanAttributes.LLM_TOP_K.value: kwargs.get("k"),
            SpanAttributes.LLM_USER.value: kwargs.get("user"),
            SpanAttributes.LLM_REQUEST_SEED.value: kwargs.get("seed"),
            SpanAttributes.LLM_FREQUENCY_PENALTY.value: kwargs.get("frequency_penalty"),
            SpanAttributes.LLM_PRESENCE_PENALTY.value: kwargs.get("presence_penalty"),
            **(extra_attributes if extra_attributes is not None else {}),
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

        span = tracer.start_span(APIS["CHAT_CREATE"]["METHOD"], kind=SpanKind.CLIENT)

        # Set the attributes on the span
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)

            # Set the response attributes
            if (hasattr(result, "generation_id")) and (
                result.generation_id is not None
            ):
                span.set_attribute(
                    SpanAttributes.LLM_GENERATION_ID.value, result.generation_id
                )
            if (hasattr(result, "response_id")) and (result.response_id is not None):
                span.set_attribute(
                    SpanAttributes.LLM_RESPONSE_ID.value, result.response_id
                )
            if (hasattr(result, "is_search_required")) and (
                result.is_search_required is not None
            ):
                span.set_attribute(
                    SpanAttributes.LLM_REQUEST_SEARCH_REQUIRED.value,
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
                                    else "USER"
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
                        span.set_attribute(
                            SpanAttributes.LLM_COMPLETIONS.value, json.dumps(responses)
                        )
                    else:
                        responses = [{"role": "CHATBOT", "content": result.text}]
                        span.set_attribute(
                            SpanAttributes.LLM_COMPLETIONS.value, json.dumps(responses)
                        )
                elif hasattr(result, "tool_calls") and result.tool_calls is not None:
                    tool_calls = []
                    for tool_call in result.tool_calls:
                        tool_calls.append(tool_call.json())
                    span.set_attribute(
                        SpanAttributes.LLM_TOOL_RESULTS.value, json.dumps(tool_calls)
                    )
                    span.set_attribute(
                        SpanAttributes.LLM_COMPLETIONS.value, json.dumps([])
                    )
                else:
                    responses = []
                    span.set_attribute(
                        SpanAttributes.LLM_COMPLETIONS.value, json.dumps(responses)
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
                                SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value,
                                usage.input_tokens or 0,
                            )
                            span.set_attribute(
                                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value,
                                usage.output_tokens or 0,
                            )

                            span.set_attribute(
                                SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
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
        prompts = [{"role": "USER", "content": message}]
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
                        item.get("role") if item.get("role") is not None else "USER"
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
        prompts = json.dumps(prompts)

        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            SpanAttributes.LANGTRACE_SDK_NAME.value: LANGTRACE_SDK_NAME,
            SpanAttributes.LANGTRACE_SERVICE_NAME.value: service_provider,
            SpanAttributes.LANGTRACE_SERVICE_TYPE.value: "llm",
            SpanAttributes.LANGTRACE_SERVICE_VERSION.value: version,
            SpanAttributes.LANGTRACE_VERSION.value: v(LANGTRACE_SDK_NAME),
            SpanAttributes.LLM_URL.value: APIS["CHAT_STREAM"]["URL"],
            SpanAttributes.LLM_PATH.value: APIS["CHAT_STREAM"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_MODEL.value: (
                kwargs.get("model", None) or "command-r"
            ),
            SpanAttributes.LLM_PROMPTS.value: prompts,
            SpanAttributes.LLM_IS_STREAMING.value: True,
            SpanAttributes.LLM_REQUEST_TEMPERATURE.value: kwargs.get("temperature"),
            SpanAttributes.LLM_REQUEST_MAX_TOKENS.value: kwargs.get("max_tokens"),
            SpanAttributes.LLM_REQUEST_TOP_P.value: kwargs.get("p"),
            SpanAttributes.LLM_TOP_K.value: kwargs.get("k"),
            SpanAttributes.LLM_USER.value: kwargs.get("user"),
            SpanAttributes.LLM_REQUEST_SEED.value: kwargs.get("seed"),
            SpanAttributes.LLM_FREQUENCY_PENALTY.value: kwargs.get("frequency_penalty"),
            SpanAttributes.LLM_PRESENCE_PENALTY.value: kwargs.get("presence_penalty"),
            **(extra_attributes if extra_attributes is not None else {}),
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

        span = tracer.start_span(APIS["CHAT_STREAM"]["METHOD"], kind=SpanKind.CLIENT)
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            span.add_event(Event.STREAM_START.value)
            try:
                for event in result:
                    if hasattr(event, "text") and event.text is not None:
                        content = event.text
                    else:
                        content = ""
                    span.add_event(
                        Event.STREAM_OUTPUT.value,
                        {
                            SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK.value: "".join(
                                content
                            )
                        },
                    )

                    if (
                        hasattr(event, "finish_reason")
                        and event.finish_reason == "COMPLETE"
                    ):
                        response = event.response
                        if (hasattr(response, "generation_id")) and (
                            response.generation_id is not None
                        ):
                            span.set_attribute(
                                SpanAttributes.LLM_GENERATION_ID.value,
                                response.generation_id,
                            )
                        if (hasattr(response, "response_id")) and (
                            response.response_id is not None
                        ):
                            span.set_attribute(
                                SpanAttributes.LLM_RESPONSE_ID.value,
                                response.response_id,
                            )
                        if (hasattr(response, "is_search_required")) and (
                            response.is_search_required is not None
                        ):
                            span.set_attribute(
                                SpanAttributes.LLM_REQUEST_SEARCH_REQUIRED.value,
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
                                            else "USER"
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
                                span.set_attribute(
                                    SpanAttributes.LLM_COMPLETIONS.value,
                                    json.dumps(responses),
                                )
                            else:
                                responses = [
                                    {"role": "CHATBOT", "content": response.text}
                                ]
                                span.set_attribute(
                                    SpanAttributes.LLM_COMPLETIONS.value,
                                    json.dumps(responses),
                                )

                        # Get the usage
                        if hasattr(response, "meta") and response.meta is not None:
                            if (
                                hasattr(response.meta, "billed_units")
                                and response.meta.billed_units is not None
                            ):
                                usage = response.meta.billed_units
                                if usage is not None:
                                    span.set_attribute(
                                        SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value,
                                        usage.input_tokens or 0,
                                    )
                                    span.set_attribute(
                                        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value,
                                        usage.output_tokens or 0,
                                    )

                                    span.set_attribute(
                                        SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
                                        (usage.input_tokens or 0)
                                        + (usage.output_tokens or 0),
                                    )

                                    span.set_attribute(
                                        "search_units",
                                        usage.search_units or 0,
                                    )

                    yield event
            finally:
                span.add_event(Event.STREAM_END.value)
                span.set_status(StatusCode.OK)
                span.end()

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method
