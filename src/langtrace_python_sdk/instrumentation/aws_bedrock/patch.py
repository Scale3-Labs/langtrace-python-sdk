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

import json

from wrapt import ObjectProxy
from .stream_body_wrapper import BufferedStreamBody
from functools import wraps
from langtrace.trace_attributes import (
    LLMSpanAttributes,
    SpanAttributes,
)
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.utils.silently_fail import silently_fail
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace.propagation import set_span_in_context
from langtrace_python_sdk.constants.instrumentation.common import (
    SERVICE_PROVIDERS,
)
from langtrace_python_sdk.constants.instrumentation.aws_bedrock import APIS
from langtrace_python_sdk.utils.llm import (
    get_extra_attributes,
    get_langtrace_attributes,
    get_llm_request_attributes,
    get_llm_url,
    get_span_name,
    set_event_completion,
    set_span_attributes,
    set_usage_attributes,
)


def converse_stream(original_method, version, tracer):
    def traced_method(wrapped, instance, args, kwargs):
        service_provider = SERVICE_PROVIDERS["AWS_BEDROCK"]

        span_attributes = {
            **get_langtrace_attributes(version, service_provider, vendor_type="llm"),
            **get_llm_request_attributes(kwargs),
            **get_llm_url(instance),
            SpanAttributes.LLM_PATH: APIS["CONVERSE_STREAM"]["ENDPOINT"],
            **get_extra_attributes(),
        }

        attributes = LLMSpanAttributes(**span_attributes)

        with tracer.start_as_current_span(
            name=get_span_name(APIS["CONVERSE_STREAM"]["METHOD"]),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, attributes)
            try:
                result = wrapped(*args, **kwargs)
                _set_response_attributes(span, kwargs, result)
                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    return traced_method


def patch_aws_bedrock(tracer, version):
    def traced_method(wrapped, instance, args, kwargs):
        if args and args[0] != "bedrock-runtime":
            return wrapped(*args, **kwargs)

        client = wrapped(*args, **kwargs)
        client.invoke_model = patch_invoke_model(client.invoke_model, tracer, version)
        client.invoke_model_with_response_stream = (
            patch_invoke_model_with_response_stream(
                client.invoke_model_with_response_stream, tracer, version
            )
        )

        client.converse = patch_converse(client.converse, tracer, version)
        client.converse_stream = patch_converse_stream(
            client.converse_stream, tracer, version
        )

        return client

    return traced_method


def patch_converse_stream(original_method, tracer, version):
    def traced_method(*args, **kwargs):
        modelId = kwargs.get("modelId")
        (vendor, _) = modelId.split(".")
        input_content = [
            {
                "role": message.get("role", "user"),
                "content": message.get("content", [])[0].get("text", ""),
            }
            for message in kwargs.get("messages", [])
        ]

        span_attributes = {
            **get_langtrace_attributes(version, vendor, vendor_type="framework"),
            **get_llm_request_attributes(kwargs, model=modelId, prompts=input_content),
            **get_llm_url(args[0] if args else None),
            **get_extra_attributes(),
        }
        with tracer.start_as_current_span(
            name=get_span_name("aws_bedrock.converse"),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, span_attributes)
            response = original_method(*args, **kwargs)

            if span.is_recording():
                set_span_streaming_response(span, response)
            return response

    return traced_method


def patch_converse(original_method, tracer, version):
    def traced_method(*args, **kwargs):
        modelId = kwargs.get("modelId")
        (vendor, _) = modelId.split(".")
        input_content = [
            {
                "role": message.get("role", "user"),
                "content": message.get("content", [])[0].get("text", ""),
            }
            for message in kwargs.get("messages", [])
        ]

        span_attributes = {
            **get_langtrace_attributes(version, vendor, vendor_type="framework"),
            **get_llm_request_attributes(kwargs, model=modelId, prompts=input_content),
            **get_llm_url(args[0] if args else None),
            **get_extra_attributes(),
        }
        with tracer.start_as_current_span(
            name=get_span_name("aws_bedrock.converse"),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, span_attributes)
            response = original_method(*args, **kwargs)

            if span.is_recording():
                _set_response_attributes(span, kwargs, response)
            return response

    return traced_method


def patch_invoke_model(original_method, tracer, version):
    def traced_method(*args, **kwargs):
        modelId = kwargs.get("modelId")
        (vendor, _) = modelId.split(".")
        span_attributes = {
            **get_langtrace_attributes(version, vendor, vendor_type="framework"),
            **get_extra_attributes(),
        }
        with tracer.start_as_current_span(
            name=get_span_name("aws_bedrock.invoke_model"),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        ) as span:
            set_span_attributes(span, span_attributes)
            response = original_method(*args, **kwargs)
            if span.is_recording():
                handle_call(span, kwargs, response)
            return response

    return traced_method


def patch_invoke_model_with_response_stream(original_method, tracer, version):
    @wraps(original_method)
    def traced_method(*args, **kwargs):
        modelId = kwargs.get("modelId")
        (vendor, _) = modelId.split(".")
        span_attributes = {
            **get_langtrace_attributes(version, vendor, vendor_type="framework"),
            **get_extra_attributes(),
        }
        span = tracer.start_span(
            name=get_span_name("aws_bedrock.invoke_model_with_response_stream"),
            kind=SpanKind.CLIENT,
            context=set_span_in_context(trace.get_current_span()),
        )
        set_span_attributes(span, span_attributes)
        response = original_method(*args, **kwargs)
        if span.is_recording():
            handle_streaming_call(span, kwargs, response)
        return response

    return traced_method


def handle_streaming_call(span, kwargs, response):

    def stream_finished(response_body):
        request_body = json.loads(kwargs.get("body"))

        (vendor, model) = kwargs.get("modelId").split(".")

        set_span_attribute(span, SpanAttributes.LLM_REQUEST_MODEL, model)
        set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, model)

        if vendor == "amazon":
            set_amazon_attributes(span, request_body, response_body)

        if vendor == "anthropic":
            if "prompt" in request_body:
                set_anthropic_completions_attributes(span, request_body, response_body)
            elif "messages" in request_body:
                set_anthropic_messages_attributes(span, request_body, response_body)

        if vendor == "meta":
            set_llama_meta_attributes(span, request_body, response_body)

        span.end()

    response["body"] = StreamingBedrockWrapper(response["body"], stream_finished)


def handle_call(span, kwargs, response):
    modelId = kwargs.get("modelId")
    (vendor, model_name) = modelId.split(".")
    response["body"] = BufferedStreamBody(
        response["body"]._raw_stream, response["body"]._content_length
    )
    request_body = json.loads(kwargs.get("body"))
    response_body = json.loads(response.get("body").read())

    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, modelId)
    set_span_attribute(span, SpanAttributes.LLM_REQUEST_MODEL, modelId)

    if vendor == "amazon":
        set_amazon_attributes(span, request_body, response_body)

    if vendor == "anthropic":
        if "prompt" in request_body:
            set_anthropic_completions_attributes(span, request_body, response_body)
        elif "messages" in request_body:
            set_anthropic_messages_attributes(span, request_body, response_body)

    if vendor == "meta":
        set_llama_meta_attributes(span, request_body, response_body)


def set_llama_meta_attributes(span, request_body, response_body):
    set_span_attribute(
        span, SpanAttributes.LLM_REQUEST_TOP_P, request_body.get("top_p")
    )
    set_span_attribute(
        span, SpanAttributes.LLM_REQUEST_TEMPERATURE, request_body.get("temperature")
    )
    set_span_attribute(
        span, SpanAttributes.LLM_REQUEST_MAX_TOKENS, request_body.get("max_gen_len")
    )
    if "invocation_metrics" in response_body:
        input_tokens = response_body.get("invocation_metrics").get("inputTokenCount")
        output_tokens = response_body.get("invocation_metrics").get("outputTokenCount")
    else:
        input_tokens = response_body.get("prompt_token_count")
        output_tokens = response_body.get("generation_token_count")

    set_usage_attributes(
        span,
        {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    )

    prompts = [
        {
            "role": "user",
            "content": request_body.get("prompt"),
        }
    ]

    completions = [
        {
            "role": "assistant",
            "content": response_body.get("generation"),
        }
    ]
    set_span_attribute(span, SpanAttributes.LLM_PROMPTS, json.dumps(prompts))
    set_event_completion(span, completions)


def set_amazon_attributes(span, request_body, response_body):
    config = request_body.get("textGenerationConfig", {})
    prompts = [
        {
            "role": "user",
            "content": request_body.get("inputText"),
        }
    ]
    if "results" in response_body:
        completions = [
            {
                "role": "assistant",
                "content": result.get("outputText"),
            }
            for result in response_body.get("results")
        ]

    else:
        completions = [
            {
                "role": "assistant",
                "content": response_body.get("outputText"),
            }
        ]
    set_span_attribute(
        span, SpanAttributes.LLM_REQUEST_MAX_TOKENS, config.get("maxTokenCount")
    )
    set_span_attribute(
        span, SpanAttributes.LLM_REQUEST_TEMPERATURE, config.get("temperature")
    )
    set_span_attribute(span, SpanAttributes.LLM_REQUEST_TOP_P, config.get("topP"))
    set_span_attribute(span, SpanAttributes.LLM_PROMPTS, json.dumps(prompts))
    input_tokens = response_body.get("inputTextTokenCount")
    if "results" in response_body:
        output_tokens = sum(
            int(result.get("tokenCount")) for result in response_body.get("results")
        )
    else:
        output_tokens = response_body.get("outputTextTokenCount")

    set_usage_attributes(
        span,
        {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    )
    set_event_completion(span, completions)


def set_anthropic_completions_attributes(span, request_body, response_body):
    set_span_attribute(
        span,
        SpanAttributes.LLM_REQUEST_MAX_TOKENS,
        request_body.get("max_tokens_to_sample"),
    )
    set_span_attribute(
        span,
        SpanAttributes.LLM_REQUEST_TEMPERATURE,
        str(request_body.get("temperature")),
    )
    set_span_attribute(
        span,
        SpanAttributes.LLM_REQUEST_TOP_P,
        str(request_body.get("top_p")),
    )
    prompts = [
        {
            "role": "user",
            "content": request_body.get("prompt"),
        }
    ]
    completions = [
        {
            "role": "assistant",
            "content": response_body.get("completion"),
        }
    ]
    set_span_attribute(span, SpanAttributes.LLM_PROMPTS, json.dumps(prompts))
    set_event_completion(span, completions)


def set_anthropic_messages_attributes(span, request_body, response_body):
    set_span_attribute(
        span,
        SpanAttributes.LLM_REQUEST_MAX_TOKENS,
        request_body.get("max_tokens_to_sample") or request_body.get("max_tokens"),
    )
    set_span_attribute(
        span,
        SpanAttributes.LLM_REQUEST_TEMPERATURE,
        str(request_body.get("temperature")),
    )
    set_span_attribute(
        span,
        SpanAttributes.LLM_REQUEST_TOP_P,
        str(request_body.get("top_p")),
    )
    set_span_attribute(
        span, SpanAttributes.LLM_PROMPTS, json.dumps(request_body.get("messages"))
    )
    set_event_completion(span, response_body.get("content"))
    set_usage_attributes(span, response_body.get("usage"))


@silently_fail
def _set_response_attributes(span, kwargs, result):
    set_span_attribute(span, SpanAttributes.LLM_RESPONSE_MODEL, kwargs.get("modelId"))
    set_span_attribute(
        span,
        SpanAttributes.LLM_TOP_K,
        kwargs.get("additionalModelRequestFields", {}).get("top_k"),
    )
    content = result.get("output", {}).get("message", {}).get("content", [])
    if len(content) > 0:
        role = result.get("output", {}).get("message", {}).get("role", "assistant")
        responses = [{"role": role, "content": c.get("text", "")} for c in content]
        set_event_completion(span, responses)

    if "usage" in result:
        set_span_attributes(
            span,
            {
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: result["usage"].get(
                    "outputTokens"
                ),
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS: result["usage"].get(
                    "inputTokens"
                ),
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS: result["usage"].get(
                    "totalTokens"
                ),
            },
        )


def set_span_streaming_response(span, response):
    streaming_response = ""
    role = None
    for event in response["stream"]:
        if "messageStart" in event:
            role = event["messageStart"]["role"]
        elif "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                streaming_response += delta["text"]
        elif "metadata" in event and "usage" in event["metadata"]:
            usage = event["metadata"]["usage"]
            set_usage_attributes(
                span,
                {
                    "input_tokens": usage.get("inputTokens"),
                    "output_tokens": usage.get("outputTokens"),
                },
            )

    if streaming_response:
        set_event_completion(
            span, [{"role": role or "assistant", "content": streaming_response}]
        )


class StreamingBedrockWrapper(ObjectProxy):
    def __init__(
        self,
        response,
        stream_done_callback=None,
    ):
        super().__init__(response)

        self._stream_done_callback = stream_done_callback
        self._accumulating_body = {"generation": ""}

    def __iter__(self):
        for event in self.__wrapped__:
            self._process_event(event)
            yield event

    def _process_event(self, event):
        chunk = event.get("chunk")
        if not chunk:
            return

        decoded_chunk = json.loads(chunk.get("bytes").decode())
        type = decoded_chunk.get("type")

        if type is None and "outputText" in decoded_chunk:
            self._stream_done_callback(decoded_chunk)
            return
        if "generation" in decoded_chunk:
            self._accumulating_body["generation"] += decoded_chunk.get("generation")

        if type == "message_start":
            self._accumulating_body = decoded_chunk.get("message")
        elif type == "content_block_start":
            self._accumulating_body["content"].append(
                decoded_chunk.get("content_block")
            )
        elif type == "content_block_delta":
            self._accumulating_body["content"][-1]["text"] += decoded_chunk.get(
                "delta"
            ).get("text")

        elif self.has_finished(type, decoded_chunk):
            self._accumulating_body["invocation_metrics"] = decoded_chunk.get(
                "amazon-bedrock-invocationMetrics"
            )
            self._stream_done_callback(self._accumulating_body)

    def has_finished(self, type, chunk):
        if type and type == "message_stop":
            return True

        if "completionReason" in chunk and chunk.get("completionReason") == "FINISH":
            return True

        if "stop_reason" in chunk and chunk.get("stop_reason") is not None:
            return True
        return False
