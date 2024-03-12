"""
This module contains functions to estimate the number of tokens in a prompt and 
to calculate the price of a model based on its usage.
"""

from tiktoken import get_encoding

from langtrace_python_sdk.constants.instrumentation.common import \
    TIKTOKEN_MODEL_MAPPING
from langtrace_python_sdk.constants.instrumentation.openai import \
    OPENAI_COST_TABLE


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
    Calculate the number of tokens in a prompt. If the model is supported by tiktoken, use it for the estimation."""
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
            (cost_table['input'] * usage['prompt_tokens'] +
             cost_table['output'] * usage['completion_tokens']) / 1000
        )
    return 0
