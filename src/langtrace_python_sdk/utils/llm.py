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

from tiktoken import get_encoding

from langtrace_python_sdk.constants.instrumentation.common import TIKTOKEN_MODEL_MAPPING
from langtrace_python_sdk.constants.instrumentation.openai import OPENAI_COST_TABLE


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
