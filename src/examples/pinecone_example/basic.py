"""
This example demonstrates how to use Pinecone with Langtrace.
"""

from langtrace_python_sdk import langtrace
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from pinecone import Pinecone


from langtrace_python_sdk import with_langtrace_root_span, send_user_feedback

_ = load_dotenv(find_dotenv())

langtrace.init()

client = OpenAI()
pinecone = Pinecone()


@with_langtrace_root_span()
def basic(span_id, trace_id):

    result = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Some random text string goes here",
        encoding_format="float",
    )

    embedding = result.data[0].embedding

    unique_id = "unique_random_id"
    data_to_upsert = {"id": unique_id, "values": embedding}

    index = pinecone.Index("test-index")
    res = index.upsert(vectors=[data_to_upsert], namespace="test-namespace")
    print("res", res)

    resp = index.query(
        vector=embedding, top_k=1, include_values=False, namespace="test-namespace"
    )
    send_user_feedback(
        {"spanId": span_id, "traceId": trace_id, "userScore": 1, "userId": "123"}
    )
    print(resp)
