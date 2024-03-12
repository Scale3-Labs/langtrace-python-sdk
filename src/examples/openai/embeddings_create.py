from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=True, log_spans_to_console=True,
               write_to_remote_url=False)
client = OpenAI()


@with_langtrace_root_span()
def embeddings_create():
    result = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Once upon a time, there was a frog.",
    )
