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


import asyncio
from functools import wraps

from opentelemetry import baggage, context, trace
from opentelemetry.trace import SpanKind

from langtrace_python_sdk.constants.instrumentation.common import \
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY


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
            new_ctx = baggage.set_baggage(
                LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, attributes
            )
            context.attach(new_ctx)
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            new_ctx = baggage.set_baggage(
                LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, attributes
            )
            context.attach(new_ctx)
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
