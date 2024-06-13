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

from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.pinecone import APIS
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


def generic_patch(operation_name, version, tracer):
    """
    A generic patch method that wraps a function with a span"""

    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[operation_name]
        service_provider = SERVICE_PROVIDERS["PINECONE"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "db.system": "pinecone",
            "db.operation": api["OPERATION"],
            "db.query": json.dumps(kwargs.get("query")),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            api["METHOD"],
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:

            if span.is_recording():
                set_span_attribute(span, "server.address", instance._config.host)
                if operation_name == "QUERY":
                    set_query_input_attributes(span, kwargs)

            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                if result:
                    if span.is_recording():
                        set_query_response_attributes(span, result)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    @silently_fail
    def set_query_input_attributes(span, kwargs):
        set_span_attribute(span, "db.query.top_k", kwargs.get("top_k"))
        set_span_attribute(span, "db.query.namespace", kwargs.get("namespace"))
        set_span_attribute(span, "db.query.id", kwargs.get("id"))
        filter = (
            json.dumps(kwargs.get("filter"))
            if isinstance(kwargs.get("filter"), dict)
            else kwargs.get("filter")
        )
        set_span_attribute(span, "db.query.filter", filter)
        set_span_attribute(
            span, "db.query.include_values", kwargs.get("include_values")
        )
        set_span_attribute(
            span, "db.query.include_metadata", kwargs.get("include_metadata")
        )

    @silently_fail
    def set_query_response_attributes(span, response):
        matches = response.get("matches")

        usage = response.get("usage")
        for match in matches:
            span.add_event(
                name="db.query.match",
                attributes={
                    "db.query.match.id": match.get("id"),
                    "db.query.match.score": match.get("score"),
                    "db.query.match.metadata": match.get("metadata"),
                    # "db.query.match.values": match.get("values"),
                },
            )

        if "read_units" in usage:
            set_span_attribute(
                span, "db.query.usage.read_units", usage.get("read_units")
            )

        if "write_units" in usage:
            set_span_attribute(
                span, "db.query.usage.write_units", usage.get("write_units")
            )

    return traced_method
