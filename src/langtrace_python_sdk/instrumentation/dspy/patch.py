import json
from importlib_metadata import version as v
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    SERVICE_PROVIDERS,
)
from opentelemetry import baggage
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode


def patch_bootstrapfewshot_optimizer(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):

        service_provider = SERVICE_PROVIDERS["DSPY"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        if instance.__class__.__name__:
            span_attributes["dspy.optimizer"] = instance.__class__.__name__
        if len(args) > 0:
            span_attributes["dspy.optimizer.module"] = args[0].__class__.__name__
            if args[0].prog:
                prog = {
                    "name": args[0].prog.__class__.__name__,
                    "signature": (
                        str(args[0].prog.signature) if args[0].prog.signature else None
                    ),
                }
                span_attributes["dspy.optimizer.module.prog"] = json.dumps(prog)
        if "metric" in instance and instance.metric:
            span_attributes["dspy.optimizer.metric"] = instance.metric.__name__
        if kwargs.get("trainset") and len(kwargs.get("trainset")) > 0:
            span_attributes["dspy.optimizer.trainset"] = str(kwargs.get("trainset"))
        config = {}
        if "metric_threshold" in instance and instance.metric_threshold:
            config["metric_threshold"] = instance.metric_threshold
        if "teacher_settings" in instance and instance.teacher_settings:
            config["teacher_settings"] = instance.teacher_settings
        if "max_bootstrapped_demos" in instance and instance.max_bootstrapped_demos:
            config["max_bootstrapped_demos"] = instance.max_bootstrapped_demos
        if "max_labeled_demos" in instance and instance.max_labeled_demos:
            config["max_labeled_demos"] = instance.max_labeled_demos
        if "max_rounds" in instance and instance.max_rounds:
            config["max_rounds"] = instance.max_rounds
        if "max_errors" in instance and instance.max_errors:
            config["max_errors"] = instance.max_errors
        if "error_count" in instance and instance.error_count:
            config["error_count"] = instance.error_count
        if config and len(config) > 0:
            span_attributes["dspy.optimizer.config"] = json.dumps(config)

        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(operation_name, kind=SpanKind.CLIENT) as span:
            _set_input_attributes(span, kwargs, attributes)

            try:
                result = wrapped(*args, **kwargs)
                if result:
                    span.set_status(Status(StatusCode.OK))

                span.end()
                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def patch_signature(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):

        service_provider = SERVICE_PROVIDERS["DSPY"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        if instance.__class__.__name__:
            span_attributes["dspy.signature.name"] = instance.__class__.__name__
            span_attributes["dspy.signature"] = str(instance)

        if kwargs and len(kwargs) > 0:
            span_attributes["dspy.signature.args"] = str(kwargs)

        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(operation_name, kind=SpanKind.CLIENT) as span:
            _set_input_attributes(span, kwargs, attributes)

            try:
                result = wrapped(*args, **kwargs)
                if result:
                    set_span_attribute(span, "dspy.signature.result", str(result))
                    span.set_status(Status(StatusCode.OK))

                span.end()
                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def patch_evaluate(operation_name, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):

        service_provider = SERVICE_PROVIDERS["DSPY"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        if "devset" in instance and instance.devset is not None:
            span_attributes["dspy.evaluate.devset"] = str(instance.devset)
        if "display" in instance and instance.display is not None:
            span_attributes["dspy.evaluate.display"] = str(instance.display)
        if "num_threads" in instance and instance.num_threads is not None:
            span_attributes["dspy.evaluate.num_threads"] = str(instance.num_threads)
        if "return_outputs" in instance and instance.return_outputs is not None:
            span_attributes["dspy.evaluate.return_outputs"] = str(
                instance.return_outputs
            )
        if "display_table" in instance and instance.display_table is not None:
            span_attributes["dspy.evaluate.display_table"] = str(instance.display_table)
        if "display_progress" in instance and instance.display_progress is not None:
            span_attributes["dspy.evaluate.display_progress"] = str(
                instance.display_progress
            )
        if "metric" in instance and instance.metric is not None:
            span_attributes["dspy.evaluate.metric"] = instance.metric.__name__
        if "error_count" in instance and instance.error_count is not None:
            span_attributes["dspy.evaluate.error_count"] = str(instance.error_count)
        if "error_lock" in instance and instance.error_lock is not None:
            span_attributes["dspy.evaluate.error_lock"] = str(instance.error_lock)
        if "max_errors" in instance and instance.max_errors is not None:
            span_attributes["dspy.evaluate.max_errors"] = str(instance.max_errors)
        if args and len(args) > 0:
            span_attributes["dspy.evaluate.args"] = str(args)

        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(operation_name, kind=SpanKind.CLIENT) as span:
            _set_input_attributes(span, kwargs, attributes)

            try:
                result = wrapped(*args, **kwargs)
                if result is not None:
                    set_span_attribute(span, "dspy.evaluate.result", str(result))
                    span.set_status(Status(StatusCode.OK))

                span.end()
                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


@silently_fail
def _set_input_attributes(span, kwargs, attributes):
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)
