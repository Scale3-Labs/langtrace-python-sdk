import asyncio
from functools import wraps

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
)
from opentelemetry import baggage, context, trace
from opentelemetry.trace import SpanKind


def with_langtrace_root_span(
    name="LangtraceRootSpan",
    kind=SpanKind.INTERNAL,
):
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            operation_name = name if name else func.__name__

            with tracer.start_as_current_span(operation_name, kind=kind):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            operation_name = name if name else func.__name__
            with tracer.start_as_current_span(operation_name, kind=kind):
                return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def with_additional_attributes(attributes={}):
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            new_ctx = baggage.set_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, attributes)
            context.attach(new_ctx)
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            new_ctx = baggage.set_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, attributes)
            context.attach(new_ctx)
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
