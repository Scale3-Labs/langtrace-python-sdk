"""
This example demonstrates how to use Pinecone with Langtrace.
"""

from langtrace_python_sdk import langtrace
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from pinecone import Pinecone

from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(
    api_key="4674df7d8113293bdb49c5e7df80eae5889e56ae748f74a1c3407c20c9521e9f",
    disable_instrumentations={"all_except": ["pinecone", "openai"]},
)

client = OpenAI()
pinecone = Pinecone()


@with_langtrace_root_span()
def basic():
    result = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Some random text string goes here",
        encoding_format="float",
    )

    embedding = result.data[0].embedding

    unique_id = "randomid"
    data_to_upsert = {"id": unique_id, "values": embedding}

    index = pinecone.Index("test-index")
    res = index.upsert(vectors=[data_to_upsert], namespace="test-namespace")
    print("res", res)

    resp = index.query(
        vector=embedding, top_k=1, include_values=False, namespace="test-namespace"
    )
    print("RESPONSE", "\n", resp)
