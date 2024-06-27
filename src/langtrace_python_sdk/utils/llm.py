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
from openai import NOT_GIVEN
from tiktoken import get_encoding

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    TIKTOKEN_MODEL_MAPPING,
)
from langtrace_python_sdk.constants.instrumentation.openai import OPENAI_COST_TABLE
from langtrace.trace_attributes import SpanAttributes
from importlib_metadata import version as v
import json
from opentelemetry import baggage


def estimate_tokens(prompt):
    """
    Estimate the number of tokens in a prompt."""
    if prompt and len(prompt) > 0:
        # Simplified token estimation: count the words.
        return len([word for word in prompt.split() if word])
    return 0


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


def set_span_attributes(span, name, value):
    if value is not None:
        if value != "":
            span.set_attribute(name, value)
    return


def get_langtrace_attributes(version, service_provider, vendor_type="llm"):
    return {
        SpanAttributes.LANGTRACE_SDK_NAME.value: LANGTRACE_SDK_NAME,
        SpanAttributes.LANGTRACE_VERSION.value: v(LANGTRACE_SDK_NAME),
        SpanAttributes.LANGTRACE_SERVICE_VERSION.value: version,
        SpanAttributes.LANGTRACE_SERVICE_NAME.value: service_provider,
        SpanAttributes.LANGTRACE_SERVICE_TYPE.value: vendor_type,
    }


def get_llm_request_attributes(kwargs, prompts=None):

    user = kwargs.get("user", "user")
    if prompts is None:
        prompts = [{"role": user, "content": kwargs.get("prompt", [])}]

    return {
        SpanAttributes.LLM_REQUEST_MODEL.value: kwargs.get("model"),
        SpanAttributes.LLM_IS_STREAMING.value: kwargs.get("stream"),
        SpanAttributes.LLM_REQUEST_TEMPERATURE.value: kwargs.get("temperature"),
        SpanAttributes.LLM_TOP_K.value: kwargs.get("n"),
        SpanAttributes.LLM_PROMPTS.value: json.dumps(prompts),
        SpanAttributes.LLM_USER.value: user,
        SpanAttributes.LLM_REQUEST_TOP_P.value: kwargs.get("top_p"),
        SpanAttributes.LLM_REQUEST_MAX_TOKENS.value: kwargs.get("max_tokens"),
        SpanAttributes.LLM_SYSTEM_FINGERPRINT.value: kwargs.get("system_fingerprint"),
    }


def get_extra_attributes():
    extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
    return extra_attributes or {}


def get_llm_url(instance):
    return {
        SpanAttributes.LLM_URL.value: get_base_url(instance),
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

    print(usage)
    set_span_attributes(
        span,
        SpanAttributes.LLM_USAGE_PROMPT_TOKENS.value,
        usage["input_tokens"] or 0,
    )

    set_span_attributes(
        span,
        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS.value,
        usage["output_tokens"] or 0,
    )

    set_span_attributes(
        span,
        SpanAttributes.LLM_USAGE_TOTAL_TOKENS.value,
        usage["input_tokens"] + usage["output_tokens"],
    )

    if "search_units" in usage:
        set_span_attributes(
            span, SpanAttributes.LLM_USAGE_SEARCH_UNITS.value, usage.search_units
        )
