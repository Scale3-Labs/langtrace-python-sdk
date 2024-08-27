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
    LLMSpanAttributes,
    SpanAttributes,
)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.common import (
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.mistral import APIS
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    StreamWrapper,
    set_span_attributes,
    set_usage_attributes,
)

from langtrace_python_sdk.instrumentation.openai.patch import extract_content


def chat_complete(original_method, version, tracer, is_async=False, is_streaming=False):
        
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["MISTRAL"]
        llm_prompts = []
        for item in kwargs.get("messages", []):
            llm_prompts.append(item)

        api = "ASYNC_CHAT_COMPLETE" if is_async else "CHAT_COMPLETE"

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, prompts=llm_prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS[api]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)


        span = tracer.start_span(
            name=get_span_name(APIS[api]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        _set_input_attributes(span, kwargs, attributes)

        try:
            result = wrapped(*args, **kwargs)
            if is_streaming:
                return StreamWrapper(
                    result,
                    span,
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


def embeddings_create(original_method, version, tracer, is_async=False):
    """
    Wrap the `create` method of the `Embeddings` class to trace it.
    """

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["MISTRAL"]

        api = "ASYNC_EMBEDDINGS_CREATE" if is_async else "EMBEDDINGS_CREATE"

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs, operation_name="embed"),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS[api]["ENDPOINT"],
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

        if kwargs.get("inputs") is not None:
            span_attributes[SpanAttributes.LLM_REQUEST_EMBEDDING_INPUTS] = json.dumps(
                [kwargs.get("inputs", [])]
            )

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS[api]["METHOD"]),
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
                raise err

    return traced_method


@silently_fail
def _set_input_attributes(span, kwargs, attributes):
    tools = []
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)

    if kwargs.get("tools") is not None:
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
            }
            for choice in result.choices
        ]
        set_event_completion(span, responses)

    # Get the usage
    if hasattr(result, "usage") and result.usage is not None:
        set_usage_attributes(span, result.usage)
