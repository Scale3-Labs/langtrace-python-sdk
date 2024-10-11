import pymongo
import os
from dotenv import load_dotenv
from openai import OpenAI
from langtrace_python_sdk import langtrace

load_dotenv()
langtrace.init()
MODEL = "text-embedding-ada-002"
openai_client = OpenAI()
client = pymongo.MongoClient(os.environ["MONGO_URI"])


# Define a function to generate embeddings
def get_embedding(text):
    """Generates vector embeddings for the given text."""
    embedding = (
        openai_client.embeddings.create(input=[text], model=MODEL).data[0].embedding
    )
    return embedding


def vector_query():
    db = client["sample_mflix"]

    embedded_movies_collection = db["embedded_movies"]

    # define pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "plot_embedding",
                "queryVector": get_embedding(
                    "A movie about a hacker that had a really rough childhood and been trying to convince his father otherwise."
                ),
                # "numCandidates": 150,
                "exact": True,
                "limit": 10,
            }
        },
        {
            "$project": {
                "_id": 0,
                "plot": 1,
                "title": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    result = embedded_movies_collection.aggregate(pipeline)
    for doc in result:
        print(doc)


if __name__ == "__main__":
    try:
        vector_query()
    except Exception as e:
        print(e)
    finally:
        client.close()
