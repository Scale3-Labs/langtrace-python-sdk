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
            "db.query": json.dumps(args[0]) if args and len(args) > 0 else "",
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

                if isinstance(result, tuple) and len(result) == 3:
                    records, result_summary, keys = result
                    _set_result_attributes(span, records, result_summary, keys)
                else:
                    res = json.dumps(result)
                    set_span_attribute(span, "neo4j.result.query_response", res)

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
            set_span_attribute(span, "db.query", query.text)
            if hasattr(query, "metadata") and query.metadata:
                set_span_attribute(span, "db.query.metadata", json.dumps(query.metadata))
            if hasattr(query, "timeout") and query.timeout:
                set_span_attribute(span, "db.query.timeout", query.timeout)
        else:
            set_span_attribute(span, "db.query", query)

    parameters = kwargs.get("parameters_", None)
    if parameters:
        try:
            set_span_attribute(span, "db.statement.parameters", json.dumps(parameters))
        except (TypeError, ValueError):
            pass

    database = kwargs.get("database_", None)
    if database:
        set_span_attribute(span, "neo4j.db.name", database)

    routing = kwargs.get("routing_", None)
    if routing:
        set_span_attribute(span, "neo4j.db.routing", str(routing))
        
        
@silently_fail
def _set_result_attributes(span, records, result_summary, keys):
    """
    Set attributes related to the query result and summary
    """
    if records is not None:
        record_count = len(records)
        set_span_attribute(span, "neo4j.result.record_count", record_count)
        if record_count > 0:
            set_span_attribute(span, "neo4j.result.records", json.dumps(records))

    if keys is not None:
        set_span_attribute(span, "neo4j.result.keys", json.dumps(keys))

    if result_summary:
        if hasattr(result_summary, "database") and result_summary.database:
            set_span_attribute(span, "neo4j.db.name", result_summary.database)

        if hasattr(result_summary, "query_type") and result_summary.query_type:
            set_span_attribute(span, "neo4j.result.query_type", result_summary.query_type)

        if hasattr(result_summary, "parameters") and result_summary.parameters:
            try:
                set_span_attribute(span, "neo4j.result.parameters", json.dumps(result_summary.parameters))
            except (TypeError, ValueError):
                pass
        
        if hasattr(result_summary, "result_available_after") and result_summary.result_available_after is not None:
            set_span_attribute(span, "neo4j.result.available_after_ms", result_summary.result_available_after)
        
        if hasattr(result_summary, "result_consumed_after") and result_summary.result_consumed_after is not None:
            set_span_attribute(span, "neo4j.result.consumed_after_ms", result_summary.result_consumed_after)

        if hasattr(result_summary, "counters") and result_summary.counters:
            counters = result_summary.counters
            if hasattr(counters, "nodes_created") and counters.nodes_created:
                set_span_attribute(span, "neo4j.result.nodes_created", counters.nodes_created)
            
            if hasattr(counters, "nodes_deleted") and counters.nodes_deleted:
                set_span_attribute(span, "neo4j.result.nodes_deleted", counters.nodes_deleted)
            
            if hasattr(counters, "relationships_created") and counters.relationships_created:
                set_span_attribute(span, "neo4j.result.relationships_created", counters.relationships_created)
            
            if hasattr(counters, "relationships_deleted") and counters.relationships_deleted:
                set_span_attribute(span, "neo4j.result.relationships_deleted", counters.relationships_deleted)
            
            if hasattr(counters, "properties_set") and counters.properties_set:
                set_span_attribute(span, "neo4j.result.properties_set", counters.properties_set)

        if hasattr(result_summary, "plan") and result_summary.plan:
            try:
                set_span_attribute(span, "neo4j.result.plan", json.dumps(result_summary.plan))
            except (TypeError, ValueError):
                pass

        if hasattr(result_summary, "notifications") and result_summary.notifications:
            try:
                set_span_attribute(span, "neo4j.result.notification_count", len(result_summary.notifications))
                set_span_attribute(span, "neo4j.result.notifications", json.dumps(result_summary.notifications))
            except (AttributeError, TypeError):
                pass