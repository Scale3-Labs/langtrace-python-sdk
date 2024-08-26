from dotenv import find_dotenv, load_dotenv
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from mistralai import Mistral

_ = load_dotenv(find_dotenv())

langtrace.init()


@with_langtrace_root_span("create_embeddings")
def embeddings_create():
    model = "mistral-embed"

    client = Mistral()

    embeddings_batch_response = client.embeddings.create(
        model=model,
        inputs=["Embed this sentence.", "As well as this one."],
    )

    print(embeddings_batch_response.data[0].embedding)
