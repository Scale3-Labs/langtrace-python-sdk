"""
This example demonstrates how to use Pinecone with Langtrace.
"""

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

from langtrace_python_sdk import (
    get_prompt_from_registry,
    langtrace,
    with_langtrace_root_span,
    with_additional_attributes,
)
from langtrace_python_sdk.utils.with_root_span import SendUserFeedback
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

_ = load_dotenv(find_dotenv())
langtrace.init()

client = OpenAI()
pinecone = Pinecone()

PINECONE_INDEX_NAME = "test-index"


def create_index():
    pinecone.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )


@with_langtrace_root_span("Pinecone Basic")
def basic():
    result = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Some random text string goes here",
        encoding_format="float",
    )

    embedding = result.data[0].embedding

    unique_id = "unique_random_id"
    data_to_upsert = {"id": unique_id, "values": embedding}

    index = pinecone.Index(PINECONE_INDEX_NAME)
    res = index.upsert(vectors=[data_to_upsert], namespace="test-namespace")

    resp = index.query(
        vector=embedding, top_k=1, include_values=False, namespace="test-namespace"
    )
    # SendUserFeedback().evaluate(
    #     {"spanId": span_id, "traceId": trace_id, "userScore": 1, "userId": "123"}
    # )
    return [res, resp]
