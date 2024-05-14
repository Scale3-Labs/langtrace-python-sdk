from openai import OpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import (
    with_additional_attributes,
    with_langtrace_root_span,
)

# _ = load_dotenv(find_dotenv())

langtrace.init(write_spans_to_console=True)
client = OpenAI(base_url="https://api.perplexity.ai", api_key="PPLX_API_KEY")


@with_additional_attributes({"user.id": "1234", "user.feedback.rating": 1})
def basic():
    response = client.chat.completions.create(
        model="pplx-70b-online",
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        stream=False,
    )
    print(response)
    return response
