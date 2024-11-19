from pymilvus import MilvusClient, model
from typing import List
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from dotenv import load_dotenv

load_dotenv()
langtrace.init()

client = MilvusClient("milvus_demo.db")

COLLECTION_NAME = "demo_collection"
embedding_fn = model.DefaultEmbeddingFunction()


def create_collection(collection_name: str = COLLECTION_NAME):
    if client.has_collection(collection_name=collection_name):
        client.drop_collection(collection_name=collection_name)

    client.create_collection(
        collection_name=collection_name,
        dimension=768,  # The vectors we will use in this demo has 768 dimensions
    )


def create_embedding(docs: List[str] = [], subject: str = "history"):
    """
    Create embeddings for the given documents.
    """

    vectors = embedding_fn.encode_documents(docs)
    # Each entity has id, vector representation, raw text, and a subject label that we use
    # to demo metadata filtering later.
    data = [
        {"id": i, "vector": vectors[i], "text": docs[i], "subject": subject}
        for i in range(len(vectors))
    ]
    # print("Data has", len(data), "entities, each with fields: ", data[0].keys())
    # print("Vector dim:", len(data[0]["vector"]))
    return data


def insert_data(collection_name: str = COLLECTION_NAME, data: List[dict] = []):
    client.insert(
        collection_name=collection_name,
        data=data,
    )


def vector_search(collection_name: str = COLLECTION_NAME, queries: List[str] = []):
    query_vectors = embedding_fn.encode_queries(queries)
    # If you don't have the embedding function you can use a fake vector to finish the demo:
    # query_vectors = [ [ random.uniform(-1, 1) for _ in range(768) ] ]

    res = client.search(
        collection_name="demo_collection",  # target collection
        data=query_vectors,  # query vectors
        limit=2,  # number of returned entities
        output_fields=["text", "subject"],  # specifies fields to be returned
        timeout=10,
        partition_names=["history"],
        anns_field="vector",
        search_params={"nprobe": 10},
    )


def query(collection_name: str = COLLECTION_NAME, query: str = ""):
    res = client.query(
        collection_name=collection_name,
        filter=query,
        # output_fields=["text", "subject"],
    )

    # print(res)


@with_langtrace_root_span("milvus_example")
def main():
    create_collection()
    # insert Alan Turing's history
    turing_data = create_embedding(
        docs=[
            "Artificial intelligence was founded as an academic discipline in 1956.",
            "Alan Turing was the first person to conduct substantial research in AI.",
            "Born in Maida Vale, London, Turing was raised in southern England.",
        ]
    )
    insert_data(data=turing_data)

    # insert AI Drug Discovery
    drug_data = create_embedding(
        docs=[
            "Machine learning has been used for drug design.",
            "Computational synthesis with AI algorithms predicts molecular properties.",
            "DDR1 is involved in cancers and fibrosis.",
        ],
        subject="biology",
    )
    insert_data(data=drug_data)

    vector_search(queries=["Who is Alan Turing?"])
    query(query="subject == 'history'")
    query(query="subject == 'biology'")


if __name__ == "__main__":
    main()
