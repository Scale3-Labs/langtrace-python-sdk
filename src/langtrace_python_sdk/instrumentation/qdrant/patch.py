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
from langtrace_python_sdk.utils.llm import get_span_name
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace_python_sdk.utils import set_span_attribute
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.qdrant import APIS
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


def collection_patch(method, version, tracer):
    """
    A generic patch method that wraps a function with a span
    """

    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[method]
        service_provider = SERVICE_PROVIDERS["QDRANT"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "db.system": "qdrant",
            "db.operation": api["OPERATION"],
            "db.query": json.dumps(kwargs.get("query")),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(api["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            collection_name = kwargs.get("collection_name") or args[0]
            operation = api["OPERATION"]
            set_span_attribute(span, "db.collection.name", collection_name)

            if operation == "add":
                _set_upload_attributes(span, args, kwargs, "documents")

            elif operation == "upsert":
                _set_upsert_attributes(span, args, kwargs)

            elif operation in ["query", "discover", "recommend", "retrieve", "search"]:
                _set_search_attributes(span, args, kwargs)
            elif operation in [
                "query_batch",
                "discover_batch",
                "recommend_batch",
                "search_batch",
            ]:
                _set_batch_search_attributes(span, args, kwargs, operation)

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


@silently_fail
def _set_upsert_attributes(span, args, kwargs):
    points = kwargs.get("points") or args[1]
    if isinstance(points, list):
        length = len(points)
    else:
        # In case of using Batch.
        length = len(points.ids)
    set_span_attribute(span, "db.upsert.points_count", length)


@silently_fail
def _set_upload_attributes(span, args, kwargs, field):
    docs = kwargs.get(field) or args[0]
    if isinstance(docs, list):
        length = len(docs)
    else:
        # In case of using Batch.
        length = len(docs.ids)

    set_span_attribute(span, f"db.upload.{field}_count", length)


@silently_fail
def _set_search_attributes(span, args, kwargs):
    limit = kwargs.get("limit") or 10
    set_span_attribute(span, "db.query.top_k", limit)


@silently_fail
def _set_batch_search_attributes(span, args, kwargs, method):
    requests = kwargs.get("requests") or []
    set_span_attribute(span, f"db.{method}.requests_count", len(requests))
