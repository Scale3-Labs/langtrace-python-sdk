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
    StreamWrapper
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


def rerank(original_method, version, tracer, v2=False):
    """Wrap the `rerank` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, operation_name="rerank"),
            **get_llm_url(instance),
            SpanAttributes.LLM_REQUEST_MODEL: kwargs.get("model") or "command-r-plus",
            SpanAttributes.LLM_URL: APIS["RERANK" if not v2 else "RERANK_V2"]["URL"],
            SpanAttributes.LLM_PATH: APIS["RERANK" if not v2 else "RERANK_V2"]["ENDPOINT"],
            SpanAttributes.LLM_REQUEST_DOCUMENTS: json.dumps(
                kwargs.get("documents"), cls=datetime_encoder
            ),
            SpanAttributes.LLM_COHERE_RERANK_QUERY: kwargs.get("query"),
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["RERANK" if not v2 else "RERANK_V2"]["METHOD"]), kind=SpanKind.CLIENT
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
                    input_tokens = int(usage.input_tokens) if usage.input_tokens else 0
                    output_tokens = int(usage.output_tokens) if usage.output_tokens else 0
                    span.set_attribute(
                        SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                        input_tokens,
                    )
                    span.set_attribute(
                        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                        output_tokens,
                    )
                    span.set_attribute(
                        SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                        input_tokens + output_tokens,
                    )
                    span.set_attribute(
                        "search_units",
                        int(usage.search_units) if usage.search_units else 0,
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


def embed(original_method, version, tracer, v2=False):
    """Wrap the `embed` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            **get_llm_url(instance),
            SpanAttributes.LLM_URL: APIS["EMBED" if not v2 else "EMBED_V2"]["URL"],
            SpanAttributes.LLM_PATH: APIS["EMBED" if not v2 else "EMBED_V2"]["ENDPOINT"],
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
            name=get_span_name(APIS["EMBED" if not v2 else "EMBED_V2"]["METHOD"]),
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
                        input_tokens = int(usage.input_tokens) if usage.input_tokens else 0
                        output_tokens = int(usage.output_tokens) if usage.output_tokens else 0
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                            input_tokens,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                            output_tokens,
                        )
                        span.set_attribute(
                            SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                            input_tokens + output_tokens,
                        )
                        span.set_attribute(
                            "search_units",
                            int(usage.search_units) if usage.search_units else 0,
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


def chat_create_v2(original_method, version, tracer, stream=False):
    """Wrap the `chat_create` method for Cohere API v2."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["COHERE"]
        
        messages = kwargs.get("messages", [])
        if kwargs.get("preamble"):
            messages = [{"role": "system", "content": kwargs["preamble"]}] + messages

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=messages),
            **get_llm_url(instance),
            SpanAttributes.LLM_REQUEST_MODEL: kwargs.get("model") or "command-r-plus",
            SpanAttributes.LLM_URL: APIS["CHAT_CREATE_V2"]["URL"],
            SpanAttributes.LLM_PATH: APIS["CHAT_CREATE_V2"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        for attr_name in ["max_input_tokens", "conversation_id", "connectors", "tools", "tool_results"]:
            value = kwargs.get(attr_name)
            if value is not None:
                if attr_name == "max_input_tokens":
                    attributes.llm_max_input_tokens = str(value)
                elif attr_name == "conversation_id":
                    attributes.conversation_id = value
                else:
                    setattr(attributes, f"llm_{attr_name}", json.dumps(value))

        span = tracer.start_span(
            name=get_span_name(APIS["CHAT_CREATE_V2"]["METHOD"]), 
            kind=SpanKind.CLIENT
        )

        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)

        try:
            result = wrapped(*args, **kwargs)

            if stream:
                return StreamWrapper(
                    result,
                    span,
                    tool_calls=kwargs.get("tools") is not None,
                )
            else:
                if hasattr(result, "id") and result.id is not None:
                    span.set_attribute(SpanAttributes.LLM_GENERATION_ID, result.id)
                    span.set_attribute(SpanAttributes.LLM_RESPONSE_ID, result.id)

                if (hasattr(result, "message") and 
                    hasattr(result.message, "content") and 
                    len(result.message.content) > 0 and
                    hasattr(result.message.content[0], "text") and
                    result.message.content[0].text is not None and
                    result.message.content[0].text != ""):
                    responses = [{
                        "role": result.message.role,
                        "content": result.message.content[0].text
                    }]
                    set_event_completion(span, responses)
                if hasattr(result, "tool_calls") and result.tool_calls is not None:
                    tool_calls = [tool_call.json() for tool_call in result.tool_calls]
                    span.set_attribute(
                        SpanAttributes.LLM_TOOL_RESULTS,
                        json.dumps(tool_calls)
                    )
                if hasattr(result, "usage") and result.usage is not None:
                    if (hasattr(result.usage, "billed_units") and 
                        result.usage.billed_units is not None):
                        usage = result.usage.billed_units
                        input_tokens = int(usage.input_tokens) if usage.input_tokens else 0
                        output_tokens = int(usage.output_tokens) if usage.output_tokens else 0
                        for metric, value in {
                            "input": input_tokens,
                            "output": output_tokens,
                            "total": input_tokens + output_tokens,
                        }.items():
                            span.set_attribute(
                                f"gen_ai.usage.{metric}_tokens",
                                int(value)
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
                                input_tokens = int(usage.input_tokens) if usage.input_tokens else 0
                                output_tokens = int(usage.output_tokens) if usage.output_tokens else 0
                                span.set_attribute(
                                    SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                                    input_tokens,
                                )
                                span.set_attribute(
                                    SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                                    output_tokens,
                                )
                                span.set_attribute(
                                    SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                                    input_tokens + output_tokens,
                                )

                                if usage.search_units is not None:
                                    span.set_attribute(
                                        "search_units",
                                        int(usage.search_units) if usage.search_units else 0,
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
