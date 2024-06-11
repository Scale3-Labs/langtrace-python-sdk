import cohere
from dotenv import find_dotenv, load_dotenv

from langtrace_python_sdk import langtrace

# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()


co = cohere.Client()


# @with_langtrace_root_span("embed_create")
def embed():
    response = co.embed(
        texts=["hello", "goodbye"],
        model="embed-english-v3.0",
        input_type="classification",
    )
    print(response)
    return response
