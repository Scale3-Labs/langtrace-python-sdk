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

from langtrace.trace_attributes import DatabaseSpanAttributes
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.chroma import APIS
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
import json
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


def collection_patch(method, version, tracer):
    """
    A generic patch method that wraps a function with a span
    """

    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[method]
        service_provider = SERVICE_PROVIDERS["CHROMA"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "db.system": "chromadb",
            "db.operation": api["OPERATION"],
            "db.query": json.dumps(kwargs.get("query")),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        if hasattr(instance, "name") and instance.name is not None:
            span_attributes["db.collection.name"] = instance.name

        attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            api["METHOD"],
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:

                operation = api["OPERATION"]
                if operation == "add":
                    _set_chroma_add_attributes(span, kwargs)
                elif operation == "get":
                    _set_chroma_get_attributes(span, kwargs)
                elif operation == "query":
                    _set_chroma_query_attributes(span, kwargs)
                elif operation == "peek":
                    _set_chroma_peek_attributes(span, kwargs)
                elif operation == "update":
                    _set_chroma_update_attributes(span, kwargs)
                elif operation == "upsert":
                    _set_chroma_upsert_attributes(span, kwargs)
                elif operation == "modify":
                    _set_chroma_modify_attributes(span, kwargs)
                elif operation == "delete":
                    _set_chroma_delete_attributes(span, kwargs)
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)

                if operation == "query":
                    events = _set_chroma_query_response(span, result)
                    for event in events:
                        span.add_event(name="db.chroma.query.result", attributes=event)

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


def get_count_or_none(value):
    return len(value) if value is not None else None


def handle_null_params(param):
    return str(param) if param else None


@silently_fail
def _set_chroma_add_attributes(span, kwargs):
    set_span_attribute(
        span, "db.chroma.add.ids_count", get_count_or_none(kwargs.get("ids"))
    )
    set_span_attribute(
        span,
        "db.chroma.add.embeddings_count",
        get_count_or_none(kwargs.get("embeddings")),
    )
    set_span_attribute(
        span,
        "db.chroma.add.metadatas_count",
        get_count_or_none(kwargs.get("metadatas")),
    )
    set_span_attribute(
        span,
        "db.chroma.add.documents_count",
        get_count_or_none(kwargs.get("documents")),
    )


@silently_fail
def _set_chroma_get_attributes(span, kwargs):
    set_span_attribute(
        span, "db.chroma.get.ids_count", get_count_or_none(kwargs.get("ids"))
    )
    set_span_attribute(
        span, "db.chroma.get.where", handle_null_params(kwargs.get("where"))
    )
    set_span_attribute(span, "db.chroma.get.limit", kwargs.get("limit"))
    set_span_attribute(span, "db.chroma.get.offset", kwargs.get("offset"))
    set_span_attribute(
        span,
        "db.chroma.get.where_document",
        handle_null_params(kwargs.get("where_document")),
    )
    set_span_attribute(
        span, "db.chroma.get.include", handle_null_params(kwargs.get("include"))
    )


@silently_fail
def _set_chroma_query_attributes(span, kwargs):
    set_span_attribute(
        span,
        "db.chroma.query.query_embeddings_count",
        get_count_or_none(kwargs.get("query_embeddings")),
    )
    set_span_attribute(
        span,
        "db.chroma.query.query_texts_count",
        get_count_or_none(kwargs.get("query_texts")),
    )
    set_span_attribute(span, "db.chroma.query.n_results", kwargs.get("n_results"))
    set_span_attribute(
        span, "db.chroma.query.where", handle_null_params(kwargs.get("where"))
    )
    set_span_attribute(
        span,
        "db.chroma.query.where_document",
        handle_null_params(kwargs.get("where_document")),
    )
    set_span_attribute(
        span, "db.chroma.query.include", handle_null_params(kwargs.get("include"))
    )


@silently_fail
def _set_chroma_peek_attributes(span, kwargs):
    set_span_attribute(span, "db.chroma.peek.limit", kwargs.get("limit"))


@silently_fail
def _set_chroma_update_attributes(span, kwargs):
    set_span_attribute(
        span, "db.chroma.update.ids_count", get_count_or_none(kwargs.get("ids"))
    )
    set_span_attribute(
        span,
        "db.chroma.update.embeddings_count",
        get_count_or_none(kwargs.get("embeddings")),
    )
    set_span_attribute(
        span,
        "db.chroma.update.metadatas_count",
        get_count_or_none(kwargs.get("metadatas")),
    )
    set_span_attribute(
        span,
        "db.chroma.update.documents_count",
        get_count_or_none(kwargs.get("documents")),
    )


@silently_fail
def _set_chroma_modify_attributes(span, kwargs):
    set_span_attribute(span, "db.chroma.modify.name", kwargs.get("name"))
    # TODO: Add metadata attribute


@silently_fail
def _set_chroma_upsert_attributes(span, kwargs):
    set_span_attribute(
        span,
        "db.chroma.upsert.embeddings_count",
        get_count_or_none(kwargs.get("embeddings")),
    )
    set_span_attribute(
        span,
        "db.chroma.upsert.metadatas_count",
        get_count_or_none(kwargs.get("metadatas")),
    )
    set_span_attribute(
        span,
        "db.chroma.upsert.documents_count",
        get_count_or_none(kwargs.get("documents")),
    )


@silently_fail
def _set_chroma_delete_attributes(span, kwargs):
    set_span_attribute(
        span, "db.chroma.delete.ids_count", get_count_or_none(kwargs.get("ids"))
    )
    set_span_attribute(
        span, "db.chroma.delete.where", handle_null_params(kwargs.get("where"))
    )
    set_span_attribute(
        span,
        "db.chroma.delete.where_document",
        handle_null_params(kwargs.get("where_document")),
    )


@silently_fail
def _set_chroma_query_response(span, result):

    attributes = []
    ids = result.get("ids")[0]
    distances = result.get("distances")[0]
    metadatas = result.get("metadatas")[0]
    documents = result.get("documents")[0]

    for idx, _ in enumerate(ids):
        attribute = {
            "id": ids[idx],
            "distance": distances[idx],
            "metadata": metadatas[idx],
            "document": documents[idx],
        }
        attributes.append(attribute)
    return attributes
