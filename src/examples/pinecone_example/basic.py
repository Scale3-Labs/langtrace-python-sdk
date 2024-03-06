"""
This example demonstrates how to use Pinecone with Langtrace.
"""
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from pinecone import Pinecone

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=True, log_spans_to_console=True,
               write_to_remote_url=False)

client = OpenAI()
pinecone = Pinecone()


@with_langtrace_root_span()
def basic():
    result = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Some random text string goes here",
        encoding_format="float"
    )

    embedding = result.data[0].embedding

    unique_id = "randomid"
    data_to_upsert = {"id": unique_id, "values": embedding}

    index = pinecone.Index("test-index")
    index.upsert(vectors=[data_to_upsert])

    resp = index.query(vector=embedding, top_k=1)
