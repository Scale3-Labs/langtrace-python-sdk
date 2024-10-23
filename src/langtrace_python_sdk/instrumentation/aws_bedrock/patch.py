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
from functools import wraps

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
from langtrace_python_sdk.constants.instrumentation.aws_bedrock import APIS
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    set_span_attributes,
)


def traced_aws_bedrock_call(api_name: str, operation_name: str):
    def decorator(method_name: str, version: str, tracer):
        def wrapper(original_method):
            @wraps(original_method)
            def wrapped_method(*args, **kwargs):
                service_provider = SERVICE_PROVIDERS["AWS_BEDROCK"]

                input_content = [
                    {
                        'role': message.get('role', 'user'),
                        'content': message.get('content', [])[0].get('text', "")
                    }
                    for message in kwargs.get('messages', [])
                ]
                
                span_attributes = {
                    **get_langtrace_attributes(version, service_provider, vendor_type="framework"),
                    **get_llm_request_attributes(kwargs, operation_name=operation_name, prompts=input_content),
                    **get_llm_url(args[0] if args else None),
                    SpanAttributes.LLM_PATH: APIS[api_name]["ENDPOINT"],
                    **get_extra_attributes(),
                }

                if api_name == "CONVERSE":
                    span_attributes.update({
                        SpanAttributes.LLM_REQUEST_MODEL: kwargs.get('modelId'),
                        SpanAttributes.LLM_REQUEST_MAX_TOKENS: kwargs.get('inferenceConfig', {}).get('maxTokens'),
                        SpanAttributes.LLM_REQUEST_TEMPERATURE: kwargs.get('inferenceConfig', {}).get('temperature'),
                        SpanAttributes.LLM_REQUEST_TOP_P: kwargs.get('inferenceConfig', {}).get('top_p'),
                    })

                attributes = LLMSpanAttributes(**span_attributes)

                with tracer.start_as_current_span(
                    name=get_span_name(APIS[api_name]["METHOD"]),
                    kind=SpanKind.CLIENT,
                    context=set_span_in_context(trace.get_current_span()),
                ) as span:
                    set_span_attributes(span, attributes)
                    try:
                        result = original_method(*args, **kwargs)
                        _set_response_attributes(span, kwargs, result)
                        span.set_status(StatusCode.OK)
                        return result
                    except Exception as err:
                        span.record_exception(err)
                        span.set_status(Status(StatusCode.ERROR, str(err)))
                        raise err

            return wrapped_method
        return wrapper
    return decorator


converse = traced_aws_bedrock_call("CONVERSE", "converse")


def converse_stream(original_method, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["AWS_BEDROCK"]
        
        span_attributes = {
            **get_langtrace_attributes
            (version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CONVERSE_STREAM"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS["CONVERSE_STREAM"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                result = wrapped(*args, **kwargs)
                _set_response_attributes(span, kwargs, result)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
            
    return traced_method


@silently_fail
def _set_response_attributes(span, kwargs, result):
    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, kwargs.get('modelId'))
    set_span_attribute(span, SpanAttributes.LLM_TOP_K, kwargs.get('additionalModelRequestFields', {}).get('top_k'))
    content = result.get('output', {}).get('message', {}).get('content', [])
    if len(content) > 0:
        role = result.get('output', {}).get('message', {}).get('role', "assistant")
        responses = [
            {"role": role, "content": c.get('text', "")}
            for c in content
        ]
        set_event_completion(span, responses)

    if 'usage' in result:
        set_span_attributes(
            span,
            {
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: result['usage'].get('outputTokens'),
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS: result['usage'].get('inputTokens'),
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS: result['usage'].get('totalTokens'),
            }
        )
