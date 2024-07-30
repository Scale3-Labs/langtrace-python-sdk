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

from dataclasses import dataclass
import json
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from langtrace.trace_attributes import FrameworkSpanAttributes
from langtrace_python_sdk.utils.llm import set_span_attributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.status import Status
from opentelemetry.trace.propagation import set_span_in_context

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from opentelemetry.trace import Tracer
from langchain_core.callbacks import BaseCallbackHandler, BaseCallbackManager
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from opentelemetry.trace import Span, Context
from opentelemetry import context as context_api


def generic_patch(
    method_name, task, tracer: Tracer, version, trace_output=True, trace_input=True
):
    """
    Wrapper function to trace a generic method.
    method_name: The name of the method to trace.
    task: The name used to identify the type of task in `generic_patch`.
    tracer: The tracer object used in `generic_patch`.
    version: The version parameter used in `generic_patch`.
    trace_output: Whether to trace the output of the patched methods.
    trace_input: Whether to trace the input of the patched methods.
    """

    def traced_method(wrapped, instance, args, kwargs):
        print("GENERIC")
        service_provider = SERVICE_PROVIDERS["LANGCHAIN_CORE"]
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

        if len(args) > 0 and trace_input:
            inputs = {}
            for arg in args:
                if isinstance(arg, dict):
                    for key, value in arg.items():
                        if isinstance(value, list):
                            for item in value:
                                inputs[key] = item.__class__.__name__
                        elif isinstance(value, str):
                            inputs[key] = value
                elif isinstance(arg, str):
                    inputs["input"] = arg
            span_attributes["langchain.inputs"] = to_json_string(inputs)

        attributes = FrameworkSpanAttributes(**span_attributes)
        span = tracer.start_span(
            name=method_name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )

        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if trace_output:
                span.set_attribute("langchain.outputs", to_json_string(result))

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


def runnable_patch(
    method_name, task, tracer: Tracer, version, trace_output=True, trace_input=True
):
    """
    Wrapper function to trace a runnable
    method_name: The name of the method to trace.
    task: The name used to identify the type of task in `generic_patch`.
    tracer: The tracer object used in `generic_patch`.
    version: The version parameter used in `generic_patch`.
    trace_output: Whether to trace the output of the patched methods.
    trace_input: Whether to trace the input of the patched methods.
    """

    def traced_method(wrapped, instance, args, kwargs):
        print("RUNNABLE")
        service_provider = SERVICE_PROVIDERS["LANGCHAIN_CORE"]
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "langchain.task.name": task,
        }

        if trace_input:
            inputs = {}
            if len(args) > 0:
                for arg in args:
                    if isinstance(arg, dict):
                        for key, value in arg.items():
                            if isinstance(value, list):
                                for item in value:
                                    inputs[key] = item.__class__.__name__
                            elif isinstance(value, str):
                                inputs[key] = value
                    elif isinstance(arg, str):
                        inputs["input"] = arg

            for field, value in (
                instance.steps.items()
                if hasattr(instance, "steps") and isinstance(instance.steps, dict)
                else {}
            ):
                inputs[field] = value.__class__.__name__

            span_attributes["langchain.inputs"] = to_json_string(inputs)

        attributes = FrameworkSpanAttributes(**span_attributes)

        span = tracer.start_span(
            name=method_name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        for field, value in attributes.model_dump(by_alias=True).items():
            if value is not None:
                span.set_attribute(field, value)
        try:
            # Attempt to call the original method
            result = wrapped(*args, **kwargs)
            if trace_output:
                outputs = {}
                if isinstance(result, dict):
                    for field, value in (
                        result.items() if hasattr(result, "items") else {}
                    ):
                        if isinstance(value, list):
                            for item in value:
                                if item.__class__.__name__ == "Document":
                                    outputs[field] = "Document"
                                else:
                                    outputs[field] = item.__class__.__name__
                        if isinstance(value, str):
                            outputs[field] = value
                span.set_attribute("langchain.outputs", to_json_string(outputs))
                if isinstance(result, str):
                    span.set_attribute("langchain.outputs", result)

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
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v != [] and v is not None]
    return {
        k: v
        for k, v in ((k, clean_empty(v)) for k, v in d.items())
        if v is not None and v != {}
    }


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
    cleaned_object = clean_empty(any_object)
    return json.dumps(cleaned_object, default=custom_serializer, indent=2)


def callback_patch(
    method_name, task, tracer: Tracer, version, trace_output=True, trace_input=True
):
    def traced_method(wrapped, instance, args, kwargs):
        if len(args) > 1:
            # args[1] is config which (may) contain the callbacks setting
            callbacks = args[1].get("callbacks", [])
        elif kwargs.get("config"):
            callbacks = kwargs.get("config", {}).get("callbacks", [])
        else:
            callbacks = []

        _add_callback(tracer, callbacks)

        if len(args) > 1:
            args[1]["callbacks"] = callbacks
        elif kwargs.get("config"):
            kwargs["config"]["callbacks"] = callbacks
        else:
            kwargs["config"] = {"callbacks": callbacks}

        return wrapped(*args, **kwargs)

    return traced_method


def _add_callback(
    tracer: Tracer, callbacks: Union[List[BaseCallbackHandler], BaseCallbackManager]
):
    cb = SyncCallBackHandler(tracer)
    if isinstance(callbacks, BaseCallbackManager):
        for c in callbacks.handlers:
            if isinstance(c, SyncCallBackHandler):
                cb = c
                break
        else:
            callbacks.add_handler(cb)
    elif isinstance(callbacks, list):
        for c in callbacks:
            if isinstance(c, SyncCallBackHandler):
                cb = c
                break
        else:
            callbacks.append(cb)


@dataclass
class SpanHolder:
    span: Span
    token: Any
    context: Context
    children: list[UUID]


class SyncCallBackHandler(BaseCallbackHandler):
    def __init__(self, tracer: Tracer):
        self.tracer = tracer
        self.spans: dict[UUID, SpanHolder] = {}

    @staticmethod
    def extract_span_name(serialized: Dict[str, Any], kwargs: Dict[str, Any]) -> str:
        try:
            return serialized["kwargs"]["name"]
        except KeyError:
            pass
        try:
            return kwargs["name"]
        except KeyError:
            return serialized["id"][-1]

    def create_span(
        self,
        run_id: UUID,
        parent_run_id: Optional[UUID],
        span_name: str,
        kind: SpanKind = SpanKind.INTERNAL,
    ) -> trace.Span:
        try:
            if parent_run_id is not None:
                print("PARENT", parent_run_id)
                print("slefspas,", self.spans)
                span = self.tracer.start_span(
                    span_name, context=self.spans[parent_run_id].context, kind=kind
                )
            else:
                span = self.tracer.start_span(span_name)

            current_context = set_span_in_context(span)
            token = context_api.attach(
                context_api.set_value(
                    "SUPPRESS_LANGUAGE_MODEL_INSTRUMENTATION_KEY", True
                )
            )
            self.spans[run_id] = SpanHolder(span, token, current_context, [])
            if parent_run_id is not None:
                self.spans[parent_run_id].children.append(run_id)

            return span
        except Exception as e:
            print("ERROR", e)

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        try:
            print("ON CHAIN START")
            span_name = self.extract_span_name(serialized, kwargs)
            span = self.create_span(run_id, parent_run_id, span_name)
            span.set_attribute(
                "entity",
                json.dumps(
                    {
                        "inputs": inputs,
                        "tags": tags,
                        "metadata": metadata,
                        "kwargs": kwargs,
                    },
                    cls=CustomJsonEncode,
                ),
            )
        except Exception as e:
            print("ERROR", e)

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        print("ON CHAIN END")

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        print("ON CHAT MODEL START")

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        print("ON LLM START")

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        print("ON LLM END")


class CustomJsonEncode(json.JSONEncoder):
    def default(self, o: Any) -> str:
        try:
            return super().default(o)
        except TypeError:
            return str(o)
