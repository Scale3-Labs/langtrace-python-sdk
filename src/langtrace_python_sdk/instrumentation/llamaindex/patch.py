"""
This module contains a generic patch method that wraps a function with a span.
"""
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.common import \
    SERVICE_PROVIDERS


def generic_patch(method, task, tracer, version):
    """
    A generic patch method that wraps a function with a span"""
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['LLAMAINDEX']
        span_attributes = {
            'langtrace.service.name': service_provider,
            'langtrace.service.type': 'framework',
            'langtrace.service.version': version,
            'langtrace.version': '1.0.0',
            'llamaindex.task.name': task,
        }

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(method, kind=SpanKind.CLIENT) as span:
            for field, value in attributes.model_dump(by_alias=True).items():
                if value is not None:
                    span.set_attribute(field, value)
            try:
                # Attempt to call the original method
                result = wrapped(*args, **kwargs)
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
