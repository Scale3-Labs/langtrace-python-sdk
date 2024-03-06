"""
This module contains the patching logic for the langchain package.
"""
import json

from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.status import Status

from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS


def generic_patch(method_name, task, tracer, version, trace_output=True, trace_input=True):
    """
    patch method for generic methods.
    """
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['LANGCHAIN']
        span_attributes = {
            'langtrace.service.name': service_provider,
            'langtrace.service.type': 'framework',
            'langtrace.service.version': version,
            'langtrace.version': '1.0.0',
            'langchain.task.name': task,
        }

        if len(args) > 0 and trace_input:
            span_attributes['langchain.inputs'] = to_json_string(args)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(method_name, kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                if trace_output:
                    span.set_attribute(
                        'langchain.outputs', to_json_string(result))

                span.set_status(StatusCode.OK)
                return result
            except Exception as e:
                # Record the exception in the span
                span.record_exception(e)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def clean_empty(d):
    """Recursively remove empty lists, empty dicts, or None elements from a dictionary."""
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v != [] and v is not None]
    return {
        k: v
        for k, v in ((k, clean_empty(v)) for k, v in d.items())
        if v is not None and v != {}
    }


def custom_serializer(obj):
    """Fallback function to convert unserializable objects."""
    if hasattr(obj, "__dict__"):
        # Attempt to serialize custom objects by their __dict__ attribute.
        return clean_empty(obj.__dict__)
    else:
        # For other types, just convert to string
        return str(obj)


def to_json_string(any_object):
    """Converts any object to a JSON-parseable string, omitting empty or None values."""
    cleaned_object = clean_empty(any_object)
    return json.dumps(cleaned_object, default=custom_serializer, indent=2)
