from tiktoken import TiktokenEncoding, get_encoding
from .constants import TIKTOKEN_MODEL_MAPPING, OPENAI_COST_TABLE

def estimate_tokens(prompt: str) -> int:
    if prompt and len(prompt) > 0:
        # Simplified token estimation: count the words.
        return len(prompt.split())
    return 0

def estimate_tokens_using_tiktoken(prompt: str, model: TiktokenEncoding) -> int:
    encoding = get_encoding(model)
    tokens = encoding.encode(prompt)
    return len(tokens)

def calculate_prompt_tokens(prompt_content: str, model: str) -> int:
    try:
        tiktoken_model = TIKTOKEN_MODEL_MAPPING[model]
        return estimate_tokens_using_tiktoken(prompt_content, tiktoken_model)
    except KeyError:
        return estimate_tokens(prompt_content)  # Fallback method

def calculate_price_from_usage(model: str, usage: dict) -> float:
    cost_table = OPENAI_COST_TABLE.get(model)
    if cost_table:
        return ((cost_table['input'] * usage['prompt_tokens'] +
                 cost_table['output'] * usage['completion_tokens']) / 1000)
    return 0
