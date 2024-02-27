import json

from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.status import Status, StatusCode

from constants import SERVICE_PROVIDERS
from instrumentation.pinecone.lib.apis import APIS


def generic_patch(tracer, method_name, task):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['LANGCHAIN']
        span_attributes = {
            "service.provider": service_provider,
        }

        if len(args) > 0:
            span_attributes[f'{task}.input'] = to_json_string(args)

        # attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(method_name, kind=SpanKind.CLIENT) as span:
            for field, value in span_attributes.items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                span.set_attribute(f'{task}.output', to_json_string(result))

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


def runnable_patch(tracer, method_name, task):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['LANGCHAIN']
        span_attributes = {
            "service.provider": service_provider,
        }

        inputs = {}
        args_list = []
        if len(args) > 0:
            for value in args:
                if isinstance(value, str):
                    args_list.append(value)
        inputs['args'] = args_list

        for field, value in instance.steps.items() if hasattr(instance, "steps") else {}:
            inputs[field] = value.__class__.__name__

        span_attributes[f'{task}.input'] = to_json_string(inputs)

        # attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(method_name, kind=SpanKind.CLIENT) as span:
            for field, value in span_attributes.items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
                outputs = {}
                if isinstance(result, dict):
                    for field, value in result.items() if hasattr(result, "items") else {}:
                        if isinstance(value, list):
                            for item in value:
                                if item.__class__.__name__ == "Document":
                                    outputs[field] = "Document"
                                else:
                                    outputs[field] = item.__class__.__name__
                        if isinstance(value, str):
                            outputs[field] = value
                span.set_attribute(f'{task}.output', to_json_string(outputs))
                if isinstance(result, str):
                    span.set_attribute(
                        f'{task}.output', result)

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
