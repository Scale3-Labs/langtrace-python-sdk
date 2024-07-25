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

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.utils import set_span_attribute
from openai import NOT_GIVEN
from tiktoken import get_encoding

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    TIKTOKEN_MODEL_MAPPING,
)
from langtrace_python_sdk.constants.instrumentation.openai import OPENAI_COST_TABLE
from langtrace.trace_attributes import SpanAttributes, Event
from importlib_metadata import version as v
import json
from opentelemetry import baggage
from opentelemetry.trace import Span
from opentelemetry.trace.status import StatusCode
import os


def estimate_tokens(prompt):
    """
    Estimate the number of tokens in a prompt."""
    if prompt and len(prompt) > 0:
        # Simplified token estimation: count the words.
        return len([word for word in prompt.split() if word])
    return 0


def set_event_completion_chunk(span: Span, chunk):
    enabled = os.environ.get("TRACE_PROMPT_COMPLETION_DATA", "true")
    if enabled.lower() == "false":
        return
    span.add_event(
        name=SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK,
        attributes={
            SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK: json.dumps(chunk),
        },
    )


def estimate_tokens_using_tiktoken(prompt, model):
    """
    Estimate the number of tokens in a prompt using tiktoken."""
    encoding = get_encoding(model)
    tokens = encoding.encode(prompt)
    return len(tokens)


def calculate_prompt_tokens(prompt_content, model):
    """
    Calculate the number of tokens in a prompt. If the model is supported by tiktoken, use it for the estimation.
    """
    try:
        tiktoken_model = TIKTOKEN_MODEL_MAPPING[model]
        return estimate_tokens_using_tiktoken(prompt_content, tiktoken_model)
    except Exception:
        return estimate_tokens(prompt_content)  # Fallback method


def calculate_price_from_usage(model, usage):
    """
    Calculate the price of a model based on its usage."""
    cost_table = OPENAI_COST_TABLE.get(model)
    if cost_table:
        return (
            cost_table["input"] * usage["prompt_tokens"]
            + cost_table["output"] * usage["completion_tokens"]
        ) / 1000
    return 0


def get_langtrace_attributes(version, service_provider, vendor_type="llm"):
    return {
        SpanAttributes.LANGTRACE_SDK_NAME: LANGTRACE_SDK_NAME,
        SpanAttributes.LANGTRACE_VERSION: v(LANGTRACE_SDK_NAME),
        SpanAttributes.LANGTRACE_SERVICE_VERSION: version,
        SpanAttributes.LANGTRACE_SERVICE_NAME: service_provider,
        SpanAttributes.LANGTRACE_SERVICE_TYPE: vendor_type,
        SpanAttributes.LLM_SYSTEM: service_provider.lower(),
    }


def get_llm_request_attributes(kwargs, prompts=None, model=None, operation_name="chat"):

    user = kwargs.get("user", None)
    if prompts is None:
        prompts = (
            [{"role": user or "user", "content": kwargs.get("prompt")}]
            if "prompt" in kwargs
            else None
        )
    top_k = (
        kwargs.get("n", None)
        or kwargs.get("k", None)
        or kwargs.get("top_k", None)
        or kwargs.get("top_n", None)
    )

    top_p = kwargs.get("p", None) or kwargs.get("top_p", None)
    tools = kwargs.get("tools", None)
    return {
        SpanAttributes.LLM_OPERATION_NAME: operation_name,
        SpanAttributes.LLM_REQUEST_MODEL: model or kwargs.get("model"),
        SpanAttributes.LLM_IS_STREAMING: kwargs.get("stream"),
        SpanAttributes.LLM_REQUEST_TEMPERATURE: kwargs.get("temperature"),
        SpanAttributes.LLM_TOP_K: top_k,
        SpanAttributes.LLM_PROMPTS: json.dumps(prompts) if prompts else None,
        SpanAttributes.LLM_USER: user,
        SpanAttributes.LLM_REQUEST_TOP_P: top_p,
        SpanAttributes.LLM_REQUEST_MAX_TOKENS: kwargs.get("max_tokens"),
        SpanAttributes.LLM_SYSTEM_FINGERPRINT: kwargs.get("system_fingerprint"),
        SpanAttributes.LLM_PRESENCE_PENALTY: kwargs.get("presence_penalty"),
        SpanAttributes.LLM_FREQUENCY_PENALTY: kwargs.get("frequency_penalty"),
        SpanAttributes.LLM_REQUEST_SEED: kwargs.get("seed"),
        SpanAttributes.LLM_TOOLS: json.dumps(tools) if tools else None,
        SpanAttributes.LLM_TOOL_CHOICE: kwargs.get("tool_choice"),
        SpanAttributes.LLM_REQUEST_LOGPROPS: kwargs.get("logprobs"),
        SpanAttributes.LLM_REQUEST_LOGITBIAS: kwargs.get("logit_bias"),
        SpanAttributes.LLM_REQUEST_TOP_LOGPROPS: kwargs.get("top_logprobs"),
    }


def get_extra_attributes():
    extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
    return extra_attributes or {}


def get_llm_url(instance):
    return {
        SpanAttributes.LLM_URL: get_base_url(instance),
    }


def get_base_url(instance):
    return (
        str(instance._client._base_url)
        if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
        else ""
    )


def is_streaming(kwargs):
    return not (
        kwargs.get("stream") is False
        or kwargs.get("stream") is None
        or kwargs.get("stream") == NOT_GIVEN
    )


def set_usage_attributes(span, usage):
    if usage is None:
        return

    input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
    output_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0

    set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
        input_tokens,
    )

    set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
        output_tokens,
    )

    set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
        input_tokens + output_tokens,
    )

    if "search_units" in usage:
        set_span_attribute(
            span, SpanAttributes.LLM_USAGE_SEARCH_UNITS, usage["search_units"]
        )


def get_tool_calls(item):
    if isinstance(item, dict):
        if "tool_calls" in item and item["tool_calls"] is not None:
            return item["tool_calls"]
        return None

    else:
        if hasattr(item, "tool_calls") and item.tool_calls is not None:
            return item.tool_calls
        return None


def set_event_completion(span: Span, result_content):
    enabled = os.environ.get("TRACE_PROMPT_COMPLETION_DATA", "true")
    if enabled.lower() == "false":
        return

    span.add_event(
        name=SpanAttributes.LLM_CONTENT_COMPLETION,
        attributes={
            SpanAttributes.LLM_COMPLETIONS: json.dumps(result_content),
        },
    )


def set_span_attributes(span: Span, attributes: dict):
    for field, value in attributes.model_dump(by_alias=True).items():
        set_span_attribute(span, field, value)


class StreamWrapper:
    span: Span

    def __init__(
        self, stream, span, prompt_tokens, function_call=False, tool_calls=False
    ):
        self.stream = stream
        self.span = span
        self.prompt_tokens = prompt_tokens
        self.function_call = function_call
        self.tool_calls = tool_calls
        self.result_content = []
        self.completion_tokens = 0
        self._span_started = False
        self.setup()

    def setup(self):
        if not self._span_started:
            self.span.add_event(Event.STREAM_START.value)
            self._span_started = True

    def cleanup(self):
        if self._span_started:
            self.span.add_event(Event.STREAM_END.value)
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                self.prompt_tokens,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                self.completion_tokens,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                self.prompt_tokens + self.completion_tokens,
            )
            set_event_completion(
                self.span,
                [
                    {
                        "role": "assistant",
                        "content": "".join(self.result_content),
                    }
                ],
            )

            self.span.set_status(StatusCode.OK)
            self.span.end()
            self._span_started = False

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    async def __aenter__(self):
        self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            chunk = next(self.stream)
            self.process_chunk(chunk)
            return chunk
        except StopIteration:
            self.cleanup()
            raise

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            chunk = await self.stream.__anext__()
            self.process_chunk(chunk)
            return chunk
        except StopAsyncIteration:
            self.cleanup()
            raise StopAsyncIteration

    def process_chunk(self, chunk):
        if hasattr(chunk, "model") and chunk.model is not None:
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_RESPONSE_MODEL,
                chunk.model,
            )

        if hasattr(chunk, "choices") and chunk.choices is not None:
            content = []
            if not self.function_call and not self.tool_calls:
                for choice in chunk.choices:
                    if choice.delta and choice.delta.content is not None:
                        token_counts = estimate_tokens(choice.delta.content)
                        self.completion_tokens += token_counts
                        content = [choice.delta.content]
            elif self.function_call:
                for choice in chunk.choices:
                    if (
                        choice.delta
                        and choice.delta.function_call is not None
                        and choice.delta.function_call.arguments is not None
                    ):
                        token_counts = estimate_tokens(
                            choice.delta.function_call.arguments
                        )
                        self.completion_tokens += token_counts
                        content = [choice.delta.function_call.arguments]
            elif self.tool_calls:
                for choice in chunk.choices:
                    if choice.delta and choice.delta.tool_calls is not None:
                        toolcalls = choice.delta.tool_calls
                        content = []
                        for tool_call in toolcalls:
                            if (
                                tool_call
                                and tool_call.function is not None
                                and tool_call.function.arguments is not None
                            ):
                                token_counts = estimate_tokens(
                                    tool_call.function.arguments
                                )
                                self.completion_tokens += token_counts
                                content.append(tool_call.function.arguments)
            set_event_completion_chunk(
                self.span,
                "".join(content) if len(content) > 0 and content[0] is not None else "",
            )
            if content:
                self.result_content.append(content[0])

        if hasattr(chunk, "text"):
            token_counts = estimate_tokens(chunk.text)
            self.completion_tokens += token_counts
            content = [chunk.text]
            set_event_completion_chunk(
                self.span,
                "".join(content) if len(content) > 0 and content[0] is not None else "",
            )

            if content:
                self.result_content.append(content[0])

        if hasattr(chunk, "usage_metadata"):
            self.completion_tokens = chunk.usage_metadata.candidates_token_count
            self.prompt_tokens = chunk.usage_metadata.prompt_token_count
