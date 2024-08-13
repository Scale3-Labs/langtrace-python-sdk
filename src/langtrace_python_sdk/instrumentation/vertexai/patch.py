import types
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS


from langtrace_python_sdk.utils.llm import (
    calculate_prompt_tokens,
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    set_span_attributes,
    set_usage_attributes,
    StreamWrapper,
)
from langtrace.trace_attributes import LLMSpanAttributes, SpanAttributes
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry.trace import Tracer, SpanKind, Span
from opentelemetry import trace
from opentelemetry.trace.propagation import set_span_in_context
from opentelemetry.trace.status import Status, StatusCode
import json


def patch_vertexai(name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["VERTEXAI"]
        prompts = serialize_prompts(args, kwargs)
        span_attributes = {
            **get_langtrace_attributes(version, service_provider),
            **get_llm_request_attributes(
                kwargs,
                prompts=prompts,
                model=get_llm_model(instance),
            ),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: "",
            **get_extra_attributes(),
        }
        attributes = LLMSpanAttributes(**span_attributes)
        span = tracer.start_span(
            name=get_span_name(name),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )

        try:
            set_span_attributes(span, attributes)
            result = wrapped(*args, **kwargs)
            if is_streaming_response(result):
                prompt_tokens = 0
                for message in kwargs.get("message", {}):
                    prompt_tokens += calculate_prompt_tokens(
                        json.dumps(message), kwargs.get("model")
                    )
                return StreamWrapper(
                    stream=result, span=span, prompt_tokens=prompt_tokens
                )
            else:
                set_response_attributes(span, result)
            span.set_status(StatusCode.OK)
            span.end()
            return result
        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


@silently_fail
def set_response_attributes(span: Span, result):

    if hasattr(result, "text"):
        set_event_completion(span, [{"role": "assistant", "content": result.text}])

    if hasattr(result, "usage_metadata"):
        usage = result.usage_metadata
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count

        set_usage_attributes(
            span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
        )

    if hasattr(result, "_prediction_response"):
        usage = result._prediction_response.metadata.get("tokenMetadata")
        input_tokens = usage.get("inputTokenCount").get("totalTokens")
        output_tokens = usage.get("outputTokenCount").get("totalTokens")
        set_usage_attributes(
            span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
        )


def is_streaming_response(response):
    return isinstance(response, types.GeneratorType) or isinstance(
        response, types.AsyncGeneratorType
    )


def get_llm_model(instance):
    llm_model = "unknown"
    if hasattr(instance, "_model_id"):
        llm_model = instance._model_id
    if hasattr(instance, "_model_name"):
        llm_model = instance._model_name.replace("publishers/google/models/", "")
    return llm_model


def serialize_prompts(args, kwargs):
    prompt = ""
    if args is not None and len(args) > 0:
        for arg in args:
            if isinstance(arg, str):
                prompt = f"{prompt}{arg}\n"
            elif isinstance(arg, list):
                for subarg in arg:
                    if type(subarg).__name__ == "Part":
                        prompt = f"{prompt}{json.dumps(subarg.to_dict())}\n"
                    else:
                        prompt = f"{prompt}{subarg}\n"
    else:
        prompt = [
            {
                "role": "user",
                "content": kwargs.get("prompt") or kwargs.get("message"),
            }
        ]
    return prompt
