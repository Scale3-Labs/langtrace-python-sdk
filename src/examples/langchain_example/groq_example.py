from dotenv import find_dotenv, load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from groq import Groq

_ = load_dotenv(find_dotenv())

from langtrace_python_sdk import langtrace

# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()

client = Groq()


def groq_basic():
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        stream=False,
        model="llama3-8b-8192",
    )
    return chat_completion


def groq_streaming():
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        stream=True,
        model="llama3-8b-8192",
    )
    for chunk in chat_completion:
        print(chunk)
