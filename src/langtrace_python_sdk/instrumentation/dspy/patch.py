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
        if hasattr(instance, 'metric'):
            span_attributes["dspy.optimizer.metric"] = getattr(instance, 'metric').__name__
        if kwargs.get("trainset") and len(kwargs.get("trainset")) > 0:
            span_attributes["dspy.optimizer.trainset"] = str(kwargs.get("trainset"))
        config = {}
        if hasattr(instance, 'metric_threshold'):
            config["metric_threshold"] = getattr(instance, 'metric_threshold')
        if hasattr(instance, 'teacher_settings'):
            config["teacher_settings"] = getattr(instance, 'teacher_settings')
        if hasattr(instance, 'max_bootstrapped_demos'):
            config["max_bootstrapped_demos"] = getattr(instance, 'max_bootstrapped_demos')
        if hasattr(instance, 'max_labeled_demos'):
            config["max_labeled_demos"] = getattr(instance, 'max_labeled_demos')
        if hasattr(instance, 'max_rounds'):
            config["max_rounds"] = getattr(instance, 'max_rounds')
        if hasattr(instance, 'max_steps'):
            config["max_errors"] = getattr(instance, 'max_errors')
        if hasattr(instance, 'error_count'):
            config["error_count"] = getattr(instance, 'error_count')
        if config and len(config) > 0:
            span_attributes["dspy.optimizer.config"] = json.dumps(config)

        # passed operation name
        opname = operation_name
        if extra_attributes is not None and "langtrace.span.name" in extra_attributes:
            # append the operation name to the span name
            opname = f"{operation_name}-{extra_attributes['langtrace.span.name']}"

        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(opname, kind=SpanKind.CLIENT) as span:
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

        # passed operation name
        opname = operation_name
        if extra_attributes is not None and "langtrace.span.name" in extra_attributes:
            # append the operation name to the span name
            opname = f"{operation_name}-{extra_attributes['langtrace.span.name']}"

        if instance.__class__.__name__:
            span_attributes["dspy.signature.name"] = instance.__class__.__name__
            span_attributes["dspy.signature"] = str(instance)

        if kwargs and len(kwargs) > 0:
            span_attributes["dspy.signature.args"] = str(kwargs)

        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(opname, kind=SpanKind.CLIENT) as span:
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

        # passed operation name
        opname = operation_name
        if extra_attributes is not None and "langtrace.span.name" in extra_attributes:
            # append the operation name to the span name
            opname = f"{operation_name}-{extra_attributes['langtrace.span.name']}"

        if hasattr(instance, "devset"):
            span_attributes["dspy.evaluate.devset"] = str(getattr(instance, "devset"))
        if hasattr(instance, "trainset"):
            span_attributes["dspy.evaluate.display"] = str(getattr(instance, "trainset"))
        if hasattr(instance, "num_threads"):
            span_attributes["dspy.evaluate.num_threads"] = str(getattr(instance, "num_threads"))
        if hasattr(instance, "return_outputs"):
            span_attributes["dspy.evaluate.return_outputs"] = str(
                getattr(instance, "return_outputs")
            )
        if hasattr(instance, "display_table"):
            span_attributes["dspy.evaluate.display_table"] = str(getattr(instance, "display_table"))
        if hasattr(instance, "display_progress"):
            span_attributes["dspy.evaluate.display_progress"] = str(
                getattr(instance, "display_progress")
            )
        if hasattr(instance, "metric"):
            span_attributes["dspy.evaluate.metric"] = getattr(instance, "metric").__name__
        if hasattr(instance, "error_count"):
            span_attributes["dspy.evaluate.error_count"] = str(getattr(instance, "error_count"))
        if hasattr(instance, "error_lock"):
            span_attributes["dspy.evaluate.error_lock"] = str(getattr(instance, "error_lock"))
        if hasattr(instance, "max_errors"):
            span_attributes["dspy.evaluate.max_errors"] = str(getattr(instance, "max_errors"))
        if args and len(args) > 0:
            span_attributes["dspy.evaluate.args"] = str(args)

        attributes = FrameworkSpanAttributes(**span_attributes)
        with tracer.start_as_current_span(opname, kind=SpanKind.CLIENT) as span:
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
