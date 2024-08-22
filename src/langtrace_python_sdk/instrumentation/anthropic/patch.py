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
from langtrace_python_sdk.utils.silently_fail import silently_fail

from langtrace_python_sdk.utils.llm import (
    StreamWrapper,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    is_streaming,
    set_event_completion,
    set_usage_attributes,
)
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from langtrace.trace_attributes import SpanAttributes

from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.constants.instrumentation.common import (
    SERVICE_PROVIDERS,
)


def messages_create(original_method, version, tracer):
    """Wrap the `messages_create` method."""

    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["ANTHROPIC"]

        # extract system from kwargs and attach as a role to the prompts
        # we do this to keep it consistent with the openai
        prompts = kwargs.get("messages", [])
        system = kwargs.get("system")
        if system:
            prompts = [{"role": "system", "content": system}] + kwargs.get(
                "messages", []
            )

        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(kwargs, prompts=prompts),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["MESSAGES_CREATE"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=get_span_name(APIS["MESSAGES_CREATE"]["METHOD"]), kind=SpanKind.CLIENT
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            set_span_attribute(span, field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            return set_response_attributes(result, span, kwargs)

        except Exception as err:
            # Record the exception in the span
            span.record_exception(err)
            # Set the span status to indicate an error
            span.set_status(Status(StatusCode.ERROR, str(err)))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    @silently_fail
    def set_response_attributes(result, span, kwargs):
        if not is_streaming(kwargs):
            if hasattr(result, "content") and result.content is not None:
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, result.model
                )
                completion = [
                    {
                        "role": result.role if result.role else "assistant",
                        "content": result.content[0].text,
                        "type": result.content[0].type,
                    }
                ]
                set_event_completion(span, completion)

            else:
                responses = []
                set_event_completion(span, responses)

            if (
                hasattr(result, "system_fingerprint")
                and result.system_fingerprint is not None
            ):
                span.set_attribute(
                    SpanAttributes.LLM_SYSTEM_FINGERPRINT,
                    result.system_fingerprint,
                )
            # Get the usage
            if hasattr(result, "usage") and result.usage is not None:
                usage = result.usage
                set_usage_attributes(span, dict(usage))

            span.set_status(StatusCode.OK)
            span.end()
            return result
        else:
            return StreamWrapper(result, span)

    # return the wrapped method
    return traced_method
