from langtrace.trace_attributes import LLMSpanAttributes, SpanAttributes
from opentelemetry import trace
from opentelemetry.trace import Span, SpanKind, Tracer
from opentelemetry.trace.propagation import set_span_in_context
from opentelemetry.trace.status import Status, StatusCode

from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    is_streaming,
    set_event_completion,
    set_event_completion_chunk,
    set_span_attributes,
    set_usage_attributes,
)


def patch_gemini(name, version, tracer: Tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["GEMINI"]
        prompts = serialize_prompts(args, kwargs, instance)
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
            name=name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )

        try:
            set_span_attributes(span, attributes)
            result = wrapped(*args, **kwargs)
            if is_streaming(kwargs):
                return build_streaming_response(span, result)

            else:
                set_response_attributes(span, result)
            span.end()
            return result
        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def apatch_gemini(name, version, tracer: Tracer):
    async def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["GEMINI"]
        prompts = serialize_prompts(args, kwargs, instance)
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
            name=name,
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )

        try:
            set_span_attributes(span, attributes)
            result = await wrapped(*args, **kwargs)
            if is_streaming(kwargs):
                return abuild_streaming_response(span, result)
            else:
                set_response_attributes(span, result)
            span.end()
            return result
        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.end()
            raise

    return traced_method


def get_llm_model(instance):
    llm_model = "unknown"
    if hasattr(instance, "_model_id"):
        llm_model = instance._model_id
    if hasattr(instance, "_model_name"):
        llm_model = instance._model_name.replace("models/", "")
    return llm_model


def serialize_prompts(args, kwargs, instance):
    prompts = []
    if (
        hasattr(instance, "_system_instruction")
        and instance._system_instruction is not None
    ):
        system_prompt = {
            "role": "system",
            "content": instance._system_instruction.__dict__["_pb"].parts[0].text,
        }
        prompts.append(system_prompt)

    if args is not None and len(args) > 0:
        content = ""
        for arg in args:
            if isinstance(arg, str):
                content = f"{content}{arg}\n"
            elif isinstance(arg, list):
                for subarg in arg:
                    content = f"{content}{subarg}\n"
        prompts.append({"role": "user", "content": content})
    return prompts


def set_response_attributes(
    span: Span,
    result,
):
    span.set_status(Status(StatusCode.OK))
    if hasattr(result, "text"):
        set_event_completion(span, [{"role": "assistant", "content": result.text}])

    if hasattr(result, "usage_metadata"):
        usage = result.usage_metadata
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count
        set_usage_attributes(
            span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
        )


def build_streaming_response(span, response):
    complete_response = ""
    for item in response:
        item_to_yield = item
        complete_response += str(item.text)
        yield item_to_yield
        set_event_completion_chunk(span, item.text)
        if hasattr(item, "usage_metadata"):
            usage = item.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            set_usage_attributes(
                span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
            )

    set_response_attributes(span, response)
    span.set_status(Status(StatusCode.OK))
    span.end()


async def abuild_streaming_response(span, response):
    complete_response = ""
    async for item in response:
        item_to_yield = item
        complete_response += str(item.text)
        yield item_to_yield
        set_event_completion_chunk(span, item.text)
        if hasattr(item, "usage_metadata"):
            usage = item.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            set_usage_attributes(
                span, {"input_tokens": input_tokens, "output_tokens": output_tokens}
            )

    set_response_attributes(span, response)
    span.set_status(Status(StatusCode.OK))
    span.end()
