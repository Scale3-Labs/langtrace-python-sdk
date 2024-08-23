import os
from langtrace_python_sdk import langtrace
from mistralai import Mistral

langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key=api_key)

embeddings_batch_response = client.embeddings.create(
    model=model,
    inputs=["Embed this sentence.", "As well as this one."],
)

print(embeddings_batch_response.data[0].embedding)
