import cohere
from dotenv import find_dotenv, load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Batch, Distance, VectorParams

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()


@with_langtrace_root_span()
def basic():
    client = QdrantClient(":memory:")
    cohere_client = cohere.Client()

    client.create_collection(
        collection_name="MyCollection4",
        vectors_config=VectorParams(
            size=1024,
            distance=Distance.COSINE,
        ),
    )

    client.upsert(
        collection_name="MyCollection4",
        points=Batch(
            ids=[1],
            vectors=cohere_client.embed(
                model="embed-english-v3.0",  # New Embed v3 model
                input_type="search_document",  # Input type for documents
                texts=["Qdrant is the a vector database written in Rust"],
            ).embeddings,
        ),
    )

    answer = client.search(
        collection_name="MyCollection4",
        query_vector=cohere_client.embed(
            model="embed-english-v3.0",  # New Embed v3 model
            input_type="search_query",  # Input type for search queries
            texts=["Which database is written in Rust?"],
        ).embeddings[0],
    )
    print(answer[0])

    return answer


basic()
