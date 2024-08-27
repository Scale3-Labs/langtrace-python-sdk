import os
from langtrace_python_sdk import with_langtrace_root_span
from mistralai import Mistral


@with_langtrace_root_span("create_embeddings")
def embeddings_create():
    model = "mistral-embed"

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    embeddings_batch_response = client.embeddings.create(
        model=model,
        inputs=["Embed this sentence.", "As well as this one."],
    )

    print(embeddings_batch_response.data[0].embedding)
