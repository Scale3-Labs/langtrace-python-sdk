"""
This module contains the patching logic for the Pinecone client."""
from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS
from langtrace_python_sdk.constants.instrumentation.pinecone import APIS


def generic_patch(original_method, method, version, tracer):
    """
    A generic patch method that wraps a function with a span"""
    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[method]
        service_provider = SERVICE_PROVIDERS['PINECONE']
        span_attributes = {
            'langtrace.service.name': service_provider,
            'langtrace.service.type': 'vectordb',
            'langtrace.service.version': version,
            'langtrace.version': '1.0.0',
            "db.system": "pinecone",
            "db.operation": api['OPERATION'],
        }

        attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(api['METHOD'], kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = original_method(instance, *args, **kwargs)
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
