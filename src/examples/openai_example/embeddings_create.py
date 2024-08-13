from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())


client = OpenAI()


@with_langtrace_root_span("Embeddings Create")
def embeddings_create():
    result = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Once upon a time, there was a pirate.",
        encoding_format="float",
    )
    return result
