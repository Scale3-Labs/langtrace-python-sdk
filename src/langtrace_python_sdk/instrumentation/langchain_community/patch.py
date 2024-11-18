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

from langtrace.trace_attributes import FrameworkSpanAttributes
from langtrace_python_sdk.utils.llm import get_span_name
from opentelemetry import baggage, trace
from opentelemetry.trace.propagation import set_span_in_context

from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from langtrace.trace_attributes import SpanAttributes

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


def generic_patch(
    method_name, task, tracer, version, trace_output=True, trace_input=True
):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["LANGCHAIN_COMMUNITY"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "langchain.task.name": task,
            **(extra_attributes if extra_attributes is not None else {}),
        }

        span_attributes["langchain.metadata"] = to_json_string(kwargs)

        if trace_input and len(args) > 0:
            span_attributes["langchain.inputs"] = to_json_string(args)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(method_name),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                if trace_output:
                    span.set_attribute("langchain.outputs", to_json_string(result))
                    prompt_tokens = (
                        instance.get_num_tokens(args[0])
                        if hasattr(instance, "get_num_tokens")
                        else None
                    )
                    completion_tokens = (
                        instance.get_num_tokens(result)
                        if hasattr(instance, "get_num_tokens")
                        else None
                    )
                    if hasattr(result, "usage"):
                        prompt_tokens = result.usage.prompt_tokens
                        completion_tokens = result.usage.completion_tokens

                    span.set_attribute(
                        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS, prompt_tokens
                    )
                    span.set_attribute(
                        SpanAttributes.LLM_USAGE_PROMPT_TOKENS, completion_tokens
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


def clean_empty(d):
    """Recursively remove empty lists, empty dicts, or None elements from a dictionary."""
    if not isinstance(d, (dict, list, tuple)):
        return d
    if isinstance(d, tuple):
        return tuple(
            val
            for val in (clean_empty(val) for val in d)
            if val != () and val is not None
        )
    if isinstance(d, list):
        return [
            val
            for val in (clean_empty(val) for val in d)
            if val != [] and val is not None
        ]
    result = {}
    for k, val in d.items():
        if isinstance(val, dict):
            val = clean_empty(val)
            if val != {} and val is not None:
                result[k] = val
        elif isinstance(val, list):
            val = [clean_empty(value) for value in val]
            if val != [] and val is not None:
                result[k] = val
        elif isinstance(val, str) and val is not None:
            if val.strip() != "":
                result[k] = val.strip()
        elif isinstance(val, object):
            # some langchain objects have a text attribute
            val = getattr(val, "text", None)
            if val is not None and val.strip() != "":
                result[k] = val.strip()
    return result


def custom_serializer(obj):
    """Fallback function to convert unserializable objects."""
    if hasattr(obj, "__dict__"):
        # Attempt to serialize custom objects by their __dict__ attribute.
        return clean_empty(obj.__dict__)
    else:
        # For other types, just convert to string
        return str(obj)


def to_json_string(any_object):
    """Converts any object to a JSON-parseable string, omitting empty or None values."""
    try:
        cleaned_object = clean_empty(any_object)
        return json.dumps(cleaned_object, default=custom_serializer, indent=2)
    except NotImplementedError:
        # Handle specific types that raise this error
        return str(any_object)  # or another appropriate fallback
    except TypeError:
        # Handle cases where obj is not serializable
        return str(any_object)
