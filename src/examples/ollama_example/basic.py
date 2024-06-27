from langtrace_python_sdk import langtrace, with_langtrace_root_span
import ollama
from ollama import AsyncClient
from dotenv import load_dotenv

load_dotenv()

langtrace.init(write_spans_to_console=False)


def chat():
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": "hi",
            },
        ],
        options={"temperature": 0.5},
        stream=True,
    )

    return response


async def async_chat():
    message = {"role": "user", "content": "Why is the sky blue?"}
    return await AsyncClient().chat(model="llama3", messages=[message])


def generate():
    return ollama.generate(model="llama3", prompt="Why is the sky blue?")


def async_generate():
    return AsyncClient().generate(model="llama3", prompt="Why is the sky blue?")


def embed():
    return ollama.embeddings(
        model="llama3",
        prompt="cat",
    )


async def async_embed():
    return await AsyncClient().embeddings(
        model="llama3",
        prompt="cat",
    )
