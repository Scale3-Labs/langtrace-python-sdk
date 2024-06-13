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
from opentelemetry.trace.propagation import set_span_in_context

from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


def patch_graph_methods(method_name, tracer, version):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["LANGGRAPH"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attr = get_atrribute_key_value(method_name, args)
        if attr is not None:
            span_attributes.update(attr)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            method_name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
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


def get_atrribute_key_value(method_name, args):
    if args is None or len(args) == 0:
        return None

    if "add_node" in method_name:
        return {
            "langgraph.node": json.dumps(
                {
                    "name": args[0],
                    "action": (
                        args[1].json()
                        if hasattr(args[1], "json")
                        else (
                            args[1].__name__
                            if hasattr(args[1], "__name__")
                            else str(args[1])
                        )
                    ),
                }
            ),
            "langgraph.task.name": "add_node",
        }
    elif "add_edge" in method_name:
        return {
            "langgraph.edge": json.dumps(
                {
                    "source": args[0],
                    "destination": args[1],
                }
            ),
            "langgraph.task.name": "add_edge",
        }
    elif "add_conditional_edges" in method_name:
        return {
            "langgraph.edge": json.dumps(
                {
                    "source": args[0],
                    "path": (
                        args[1].json()
                        if hasattr(args[1], "json")
                        else (
                            args[1].__name__
                            if hasattr(args[1], "__name__")
                            else str(args[1])
                        )
                    ),
                    "path_map": args[2],
                }
            ),
            "langgraph.task.name": "add_conditional_edges",
        }
    elif "set_entry_point" in method_name:
        return {
            "langgraph.entrypoint": args[0],
            "langgraph.task.name": "set_entry_point",
        }
    elif "set_finish_point" in method_name:
        return {
            "langgraph.finishpoint": args[0],
            "langgraph.task.name": "set_finish_point",
        }
    else:
        return None
