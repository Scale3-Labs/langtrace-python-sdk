import json

from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, SERVICE_PROVIDERS)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.llm import get_span_name, set_span_attributes
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs


def patch_run(operation_name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        print("\n\n\nTracing CrewaiTools\n\n\n")
        service_provider = SERVICE_PROVIDERS["CREWAI"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        inputs = {}
        if len(args) > 0:
            inputs["args"] = serialize_args(*args)
        if len(kwargs) > 0:
            inputs["kwargs"] = serialize_kwargs(**kwargs)
        span_attributes["crewai_tools.tools.serper_dev_tool.inputs"] = json.dumps(inputs)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            get_span_name(operation_name), kind=SpanKind.CLIENT
        ) as span:

            try:
                set_span_attributes(span, attributes)
                result = wrapped(*args, **kwargs)
                if result is not None and len(result) > 0:
                    set_span_attribute(
                        span, "crewai_tools.tools.serper_dev_tool.outputs", str(result)
                    )
                if result:
                    span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method
