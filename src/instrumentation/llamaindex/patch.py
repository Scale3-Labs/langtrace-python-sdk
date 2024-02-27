from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.status import Status, StatusCode

from constants import SERVICE_PROVIDERS


def generic_patch(name, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS['LLAMAINDEX']
        span_attributes = {
            "service.provider": service_provider
        }

        with tracer.start_as_current_span(name, kind=SpanKind.CLIENT) as span:
            for field, value in span_attributes.items():
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
