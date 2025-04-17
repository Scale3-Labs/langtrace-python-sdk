import json
from typing import Any, Callable, List

from importlib_metadata import version as v
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry import baggage
from opentelemetry.trace import SpanKind, Tracer
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, SERVICE_PROVIDERS)
from langtrace_python_sdk.instrumentation.openai.types import \
    ChatCompletionsCreateKwargs
from langtrace_python_sdk.utils.llm import set_span_attributes
from langtrace_python_sdk.utils.misc import serialize_args, serialize_kwargs


def generic_patch(version: str, tracer: Tracer) -> Callable:
    """Wrap the `prompt` method of the `TLM` class to trace it."""

    def traced_method(
        wrapped: Callable,
        instance: Any,
        args: List[Any],
        kwargs: ChatCompletionsCreateKwargs,
    ) -> Any:
        service_provider = SERVICE_PROVIDERS["CLEANLAB"]
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        span_attributes = {
            "langtrace.sdk.name": "langtrace-python-sdk",
            "langtrace.service.name": service_provider,
            "langtrace.service.type": "framework",
            "langtrace.service.version": version,
            "langtrace.version": v(LANGTRACE_SDK_NAME),
            **(extra_attributes if extra_attributes is not None else {}),
        }

        span_attributes["tlm.metadata"] = serialize_kwargs(**kwargs)
        span_attributes["tlm.inputs"] = serialize_args(*args)

        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=f"tlm.{wrapped.__name__}", kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                result = wrapped(*args, **kwargs)
                if result:
                    # Handle result serialization based on its type
                    if hasattr(result, 'model_dump_json'):
                        # For Pydantic models
                        result_json = json.loads(result.model_dump_json())
                    elif isinstance(result, dict):
                        # For dictionary results
                        result_json = result
                    else:
                        # For other types, try to convert to dict or use string representation
                        try:
                            result_json = json.loads(json.dumps(result, default=str))
                        except Exception:  # pylint: disable=W0702, W0718
                            result_json = str(result)

                    span.set_attribute("tlm.result", str(result_json))
                    trustworthiness_score = result_json["trustworthiness_score"]
                    log = result_json["log"]
                    span.set_attribute("tlm.trustworthiness_score", str(trustworthiness_score))
                    span.set_attribute("tlm.explanation", str(log.get("explanation", "")))
                    span.set_status(Status(StatusCode.OK))

                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    return traced_method
