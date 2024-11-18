from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry.trace import Tracer
from opentelemetry.trace import SpanKind
from langtrace_python_sdk.utils import handle_span_error, set_span_attribute
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    set_span_attributes,
)
import json


def generic_patch(api, version: str, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        span_name = api["SPAN_NAME"]
        operation = api["OPERATION"]
        with tracer.start_as_current_span(span_name, kind=SpanKind.CLIENT) as span:
            try:
                span_attributes = {
                    "db.system": "milvus",
                    "db.operation": operation,
                    "db.name": kwargs.get("collection_name", None),
                    **get_extra_attributes(),
                }

                if operation == "create_collection":
                    set_create_collection_attributes(span_attributes, kwargs)

                elif operation == "insert" or operation == "upsert":
                    set_insert_or_upsert_attributes(span_attributes, kwargs)

                elif operation == "search":
                    set_search_attributes(span_attributes, kwargs)

                elif operation == "query":
                    set_query_attributes(span_attributes, kwargs)

                set_span_attributes(span, span_attributes)
                result = wrapped(*args, **kwargs)

                if operation == "query":
                    set_query_response_attributes(span, result)

                if operation == "search":
                    set_search_response_attributes(span, result)
                return result
            except Exception as err:
                handle_span_error(span, err)
                raise

    return traced_method


@silently_fail
def set_create_collection_attributes(span_attributes, kwargs):
    span_attributes["db.dimension"] = kwargs.get("dimension", None)


@silently_fail
def set_insert_or_upsert_attributes(span_attributes, kwargs):
    data = kwargs.get("data")
    timeout = kwargs.get("timeout")
    partition_name = kwargs.get("partition_name")

    span_attributes["db.num_entities"] = len(data) if data else None
    span_attributes["db.timeout"] = timeout
    span_attributes["db.partition_name"] = partition_name


@silently_fail
def set_search_attributes(span_attributes, kwargs):
    data = kwargs.get("data")
    filter = kwargs.get("filter")
    limit = kwargs.get("limit")
    output_fields = kwargs.get("output_fields")
    search_params = kwargs.get("search_params")
    timeout = kwargs.get("timeout")
    partition_names = kwargs.get("partition_names")
    anns_field = kwargs.get("anns_field")
    span_attributes["db.num_queries"] = len(data) if data else None
    span_attributes["db.filter"] = filter
    span_attributes["db.limit"] = limit
    span_attributes["db.output_fields"] = json.dumps(output_fields)
    span_attributes["db.search_params"] = json.dumps(search_params)
    span_attributes["db.partition_names"] = json.dumps(partition_names)
    span_attributes["db.anns_field"] = anns_field
    span_attributes["db.timeout"] = timeout


@silently_fail
def set_query_attributes(span_attributes, kwargs):
    filter = kwargs.get("filter")
    output_fields = kwargs.get("output_fields")
    timeout = kwargs.get("timeout")
    partition_names = kwargs.get("partition_names")
    ids = kwargs.get("ids")

    span_attributes["db.filter"] = filter
    span_attributes["db.output_fields"] = output_fields
    span_attributes["db.timeout"] = timeout
    span_attributes["db.partition_names"] = partition_names
    span_attributes["db.ids"] = ids


@silently_fail
def set_query_response_attributes(span, result):
    set_span_attribute(span, name="db.num_matches", value=len(result))
    for match in result:
        span.add_event(
            "db.query.match",
            attributes=match,
        )


@silently_fail
def set_search_response_attributes(span, result):
    for res in result:
        for match in res:
            span.add_event(
                "db.search.match",
                attributes={
                    "id": match["id"],
                    "distance": str(match["distance"]),
                    "entity": json.dumps(match["entity"]),
                },
            )
