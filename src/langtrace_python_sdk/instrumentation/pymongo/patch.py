from langtrace_python_sdk.utils.llm import (
    get_langtrace_attributes,
    get_span_name,
    set_span_attributes,
    set_span_attribute,
)
from langtrace_python_sdk.utils import deduce_args_and_kwargs, handle_span_error
from opentelemetry.trace import SpanKind
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace.trace_attributes import DatabaseSpanAttributes

import json


def generic_patch(name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        database = instance.database.__dict__
        span_attributes = {
            **get_langtrace_attributes(
                version=version,
                service_provider=SERVICE_PROVIDERS["MONGODB"],
                vendor_type="vectordb",
            ),
            "db.system": "mongodb",
            "db.query": "aggregate",
        }

        attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(name), kind=SpanKind.CLIENT
        ) as span:
            if span.is_recording():
                set_input_attributes(
                    span, deduce_args_and_kwargs(wrapped, *args, **kwargs)
                )
                set_span_attributes(span, attributes)

            try:
                result = wrapped(*args, **kwargs)
                for doc in result:
                    if span.is_recording():
                        span.add_event(
                            name="db.query.match",
                            attributes={**doc},
                        )
                return result
            except Exception as err:
                handle_span_error(span, err)
                raise

    return traced_method


def set_input_attributes(span, args):
    pipeline = args.get("pipeline", None)
    for stage in pipeline:
        for k, v in stage.items():
            if k == "$vectorSearch":
                set_span_attribute(span, "db.index", v.get("index", None))
                set_span_attribute(span, "db.path", v.get("path", None))
                set_span_attribute(span, "db.top_k", v.get("numCandidates"))
                set_span_attribute(span, "db.limit", v.get("limit"))
            else:
                set_span_attribute(span, k, json.dumps(v))
