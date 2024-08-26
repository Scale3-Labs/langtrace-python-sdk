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

from importlib_metadata import version as v
from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry import baggage, trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation import set_span_in_context
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.weaviate import APIS
from langtrace_python_sdk.utils.llm import get_span_name
from langtrace_python_sdk.utils.misc import extract_input_params, to_iso_format

# Predefined metadata response attributes
METADATA_ATTRIBUTES = [
    "creation_time",
    "last_update_time",
    "distance",
    "certainty",
    "score",
    "explain_score",
    "is_consistent",
    "rerank_score",
]


def extract_inputs(args, kwargs):
    extracted_params = {}
    kwargs_without_properties = {k: v for k, v in kwargs.items() if k != "properties"}
    extracted_params.update(extract_input_params(args, kwargs_without_properties))

    if kwargs.get("properties", None):
        extracted_params["properties"] = []
        for each_prop in kwargs.get("properties"):
            if hasattr(each_prop, "_to_dict"):
                # append properties to extracted_params
                extracted_params["properties"].append(each_prop._to_dict())

        extracted_params["properties"] = json.dumps(extracted_params["properties"])
    return extracted_params


def extract_metadata(metadata):
    # Extraction response Query metadata
    extracted_metadata = {
        attr: (
            to_iso_format(getattr(metadata, attr))
            if "time" in attr
            else getattr(metadata, attr)
        )
        for attr in METADATA_ATTRIBUTES
        if hasattr(metadata, attr)
    }

    return {k: v for k, v in extracted_metadata.items() if v is not None}


def aggregate_responses(result):
    all_responses = []

    if hasattr(result, "objects") and result.objects is not None:
        for each_obj in result.objects:
            # Loop for multiple object responses
            response_attributes = get_response_object_attributes(each_obj)
            all_responses.append(response_attributes)
    else:
        # For single object responses
        all_responses = get_response_object_attributes(result)

    return json.dumps(all_responses)


def get_response_object_attributes(response_object):

    response_attributes = {
        **response_object.properties,
        "uuid": str(response_object.uuid) if hasattr(response_object, "uuid") else None,
        "collection": (
            response_object.collection
            if hasattr(response_object, "collection")
            else None
        ),
        "vector": (
            response_object.vector if hasattr(response_object, "vector") else None
        ),
        "references": (
            response_object.references
            if hasattr(response_object, "references")
            else None
        ),
        "metadata": (
            extract_metadata(response_object.metadata)
            if hasattr(response_object, "metadata")
            else None
        ),
    }
    response_attributes = {
        k: v for k, v in response_attributes.items() if v is not None
    }
    return response_attributes


def create_traced_method(method_name, version, tracer, get_collection_name=None):
    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[method_name]
        service_provider = SERVICE_PROVIDERS["WEAVIATE"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)

        collection_name = (
            get_collection_name(instance, kwargs)
            if get_collection_name
            else instance._name
        )

        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "vectordb",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            "db.system": "weaviate",
            "db.operation": api["OPERATION"],
            "db.collection.name": collection_name,
            "db.query": json.dumps(extract_inputs(args, kwargs)),
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
                if api["OPERATION"] in ["query", "generate"]:
                    span.add_event(
                        name="db.response",
                        attributes={"db.response": aggregate_responses(result)},
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


def generic_query_patch(method_name, version, tracer):
    return create_traced_method(method_name, version, tracer)


def generic_collection_patch(method_name, version, tracer):
    return create_traced_method(
        method_name,
        version,
        tracer,
        get_collection_name=lambda instance, kwargs: kwargs.get("name"),
    )
