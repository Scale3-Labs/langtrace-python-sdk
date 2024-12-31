import os
from langtrace_python_sdk import langtrace
import cohere

langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

docs = [
    "Carson City is the capital city of the American state of Nevada.",
    "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",
    "Capitalization or capitalisation in English grammar is the use of a capital letter at the start of a word. English usage varies from capitalization in other languages.",
    "Washington, D.C. (also known as simply Washington or D.C., and officially as the District of Columbia) is the capital of the United States. It is a federal district.",
    "Capital punishment has existed in the United States since beforethe United States was a country. As of 2017, capital punishment is legal in 30 of the 50 states.",
]

def rerank_v2():
    response = co.rerank(
        model="rerank-v3.5",
        query="What is the capital of the United States?",
        documents=docs,
        top_n=3,
    )
    print(response)
