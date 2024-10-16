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

import re
from importlib_metadata import version as v
from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind,Tracer
from opentelemetry.trace.propagation import set_span_in_context
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.pgvector import APIS
from langtrace_python_sdk.utils.llm import get_span_name
from langtrace_python_sdk.utils.misc import extract_input_params, to_iso_format


# Utility function to extract table name
def extract_table_name(query):
    # This regex assumes basic SQL queries like SELECT, INSERT INTO, UPDATE, DELETE FROM
    match = re.search(r'(from|into|update|delete\s+from)\s+(\w+)', query, re.IGNORECASE)
    if match:
        return match.group(2)
    return None


def generic_patch(method_name, version, tracer: Tracer):

    def traced_method(wrapped, instance, args, kwargs): 
        query = args[0]
        params = args[1] if len(args) > 1 else None 
        api = APIS[method_name]
        service_provider = SERVICE_PROVIDERS["PGVECTOR"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "db.system": "pgvector",
            "db.operation": api["OPERATION"],
            "db.collection.name": extract_table_name(query),
            "db.namespace": instance.connection.info.dbname,
            "db.query": str(query),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = DatabaseSpanAttributes(**span_attributes)

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
