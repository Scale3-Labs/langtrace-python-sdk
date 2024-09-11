from langtrace_python_sdk.utils.llm import (
    get_langtrace_attributes,
    get_extra_attributes,
    get_span_name,
    set_span_attributes,
    get_llm_request_attributes,
    set_event_completion,
    set_usage_attributes,
)
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace.trace_attributes import FrameworkSpanAttributes
from opentelemetry.trace.status import Status, StatusCode
from langtrace.trace_attributes import SpanAttributes
from opentelemetry.trace import Tracer, SpanKind

from langtrace_python_sdk.utils import deduce_args_and_kwargs, set_span_attribute
import json


def patch_initiate_chat(name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        all_params = deduce_args_and_kwargs(wrapped, *args, **kwargs)
        all_params["recipient"] = json.dumps(parse_agent(all_params.get("recipient")))
        span_attributes = {
            **get_langtrace_attributes(
                service_provider=SERVICE_PROVIDERS["AUTOGEN"],
                version=version,
                vendor_type="framework",
            ),
            "sender": json.dumps(parse_agent(instance)),
            **all_params,
        }
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(name), kind=SpanKind.CLIENT
        ) as span:
            try:
                set_span_attributes(span, attributes)
                result = wrapped(*args, **kwargs)
                # set_response_attributes(span, result)
                return result
            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def patch_generate_reply(name, version, tracer: Tracer):

    def traced_method(wrapped, instance, args, kwargs):

        llm_config = instance.llm_config
        kwargs = {
            **kwargs,
            **llm_config.get("config_list")[0],
        }
        service_provider = SERVICE_PROVIDERS["AUTOGEN"]

        span_attributes = {
            **get_langtrace_attributes(
                version=version,
                service_provider=service_provider,
                vendor_type="framework",
            ),
            **get_llm_request_attributes(
                kwargs,
                prompts=kwargs.get("messages"),
            ),
            **get_extra_attributes(),
        }
        attributes = FrameworkSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(name), kind=SpanKind.CLIENT
        ) as span:
            try:

                result = wrapped(*args, **kwargs)
                
                # if caching is disabled, return result as langtrace will instrument the rest.
                if "cache_seed" in llm_config and llm_config.get("cache_seed") is None:
                    return result

                set_span_attributes(span, attributes)
                set_event_completion(span, [{"role": "assistant", "content": result}])
                total_cost, response_model = list(instance.get_total_usage().keys())
                set_span_attribute(
                    span, SpanAttributes.LLM_RESPONSE_MODEL, response_model
                )
                set_usage_attributes(
                    span, instance.get_total_usage().get(response_model)
                )

                return result

            except Exception as err:
                # Record the exception in the span
                span.record_exception(err)

                # Set the span status to indicate an error
                span.set_status(Status(StatusCode.ERROR, str(err)))

                # Reraise the exception to ensure it's not swallowed
                raise

    return traced_method


def set_response_attributes(span, result):
    summary = getattr(result, "summary", None)
    if summary:
        set_span_attribute(span, "autogen.chat.summary", summary)


def parse_agent(agent):

    return {
        "name": getattr(agent, "name", None),
        "description": getattr(agent, "description", None),
        "system_message": str(getattr(agent, "system_message", None)),
        "silent": getattr(agent, "silent", None),
        "llm_config": str(getattr(agent, "llm_config", None)),
        "human_input_mode": getattr(agent, "human_input_mode", None),
    }
