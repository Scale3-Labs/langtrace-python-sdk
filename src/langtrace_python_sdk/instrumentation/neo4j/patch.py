"""
Copyright (c) 2025 Scale3 Labs

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

from langtrace_python_sdk.utils.llm import get_span_name
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace.trace_attributes import DatabaseSpanAttributes
from langtrace_python_sdk.utils import set_span_attribute
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.neo4j import APIS
from importlib.metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


def driver_patch(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        
        api = APIS[operation_name]
        service_provider = SERVICE_PROVIDERS.get("NEO4J", "neo4j")
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "db.system": "neo4j",
            "db.operation": api["OPERATION"],
            "db.query": json.dumps(kwargs),
            **(extra_attributes if extra_attributes is not None else {}),
        }
        
        attributes = DatabaseSpanAttributes(**span_attributes)
        
        with tracer.start_as_current_span(
            name=get_span_name(api["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)

            if operation_name == "EXECUTE_QUERY":
                _set_execute_query_attributes(span, args, kwargs)
            
            try:
                result = wrapped(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
    
    return traced_method


@silently_fail
def _set_execute_query_attributes(span, args, kwargs):
    query = args[0] if args else kwargs.get("query_", None)
    if query:
        if hasattr(query, "text"):
            set_span_attribute(span, "db.statement", query.text)
            set_span_attribute(span, "db.query", query.text)
            if hasattr(query, "metadata") and query.metadata:
                set_span_attribute(span, "db.query.metadata", json.dumps(query.metadata))
            if hasattr(query, "timeout") and query.timeout:
                set_span_attribute(span, "db.query.timeout", query.timeout)
        else:
            set_span_attribute(span, "db.statement", query)
            set_span_attribute(span, "db.query", query)

    parameters = kwargs.get("parameters_", None)
    if parameters:
        try:
            set_span_attribute(span, "db.statement.parameters", json.dumps(parameters))
        except (TypeError, ValueError):
            pass

    database = kwargs.get("database_", None)
    if database:
        set_span_attribute(span, "db.name", database)

    routing = kwargs.get("routing_", None)
    if routing:
        set_span_attribute(span, "db.routing", str(routing))