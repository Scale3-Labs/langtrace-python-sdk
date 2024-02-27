from langtrace.trace_attributes import DatabaseSpanAttributes
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.status import Status, StatusCode

from constants import SERVICE_PROVIDERS
from instrumentation.chroma.lib.apis import APIS


def collection_patch(method, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        api = APIS[method]
        service_provider = SERVICE_PROVIDERS['CHROMA']
        span_attributes = {
            "service.provider": service_provider,
            "db.system": "chromadb",
            "db.operation": api['OPERATION'],
        }

        if hasattr(instance, 'name') and instance.get('name') is not None:
            span_attributes["db.chromadb.collection"] = str(instance.name)

        attributes = DatabaseSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(api["METHOD"], kind=SpanKind.CLIENT) as span:
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
