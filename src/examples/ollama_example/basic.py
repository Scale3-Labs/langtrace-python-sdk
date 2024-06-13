from langtrace_python_sdk import langtrace, with_langtrace_root_span
import ollama
from ollama import AsyncClient
from dotenv import load_dotenv

load_dotenv()

langtrace.init(write_spans_to_console=True)


@with_langtrace_root_span("Ollama")
def basic():
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": "hi",
            },
        ],
        stream=True,
    )
    print("", response)

    # return response["message"]["content"]


async def async_basic():
    message = {"role": "user", "content": "Why is the sky blue?"}
    response = await AsyncClient().chat(model="llama3", messages=[message])
    return response


def generate():
    return ollama.generate(model="llama3", prompt="Why is the sky blue?")
