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

from typing import Any, Callable, List, Iterator, Union
from langtrace.trace_attributes import SpanAttributes, LLMSpanAttributes
import json

from langtrace_python_sdk.utils.llm import (
    StreamWrapper,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    set_span_attributes,
    set_usage_attributes,
    set_span_attribute,
)
from opentelemetry.trace import Span, Tracer, SpanKind
from opentelemetry.trace.status import StatusCode
from langtrace_python_sdk.constants.instrumentation.anthropic import APIS
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.instrumentation.anthropic.types import (
    StreamingResult,
    ResultType,
    MessagesCreateKwargs,
)


def messages_create(version: str, tracer: Tracer) -> Callable[..., Any]:
    """Wrap the `messages_create` method."""

    def traced_method(
        wrapped: Callable[..., Any],
        instance: Any,
        args: List[Any],
        kwargs: MessagesCreateKwargs,
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["ANTHROPIC"]

        # Extract system from kwargs and attach as a role to the prompts
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
        set_span_attributes(span, attributes)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            return set_response_attributes(result, span)

        except Exception as err:
            # Record the exception in the span
            span.record_exception(err)
            # Set the span status to indicate an error
            span.set_status(StatusCode.ERROR, str(err))
            # Reraise the exception to ensure it's not swallowed
            span.end()
            raise

    def set_response_attributes(
        result: Union[ResultType, StreamingResult], span: Span
    ) -> Any:
        if not isinstance(result, Iterator):
            if hasattr(result, "content") and result.content is not None:
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, result.model
                )
                if hasattr(result, "content") and result.content[0] is not None:
                    content = result.content[0]
                    typ = content.type
                    role = result.role if result.role else "assistant"
                    if typ == "tool_result" or typ == "tool_use":
                        content = content.json()  # type: ignore
                        set_span_attribute(
                            span, SpanAttributes.LLM_TOOL_RESULTS, json.dumps(content)
                        )
                    if typ == "text":
                        content = result.content[0].text
                        set_event_completion(
                            span, [{"type": typ, "role": role, "content": content}]
                        )

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
                set_usage_attributes(span, vars(usage))

            span.set_status(StatusCode.OK)
            span.end()
            return result
        else:
            return StreamWrapper(result, span)

    # return the wrapped method
    return traced_method
