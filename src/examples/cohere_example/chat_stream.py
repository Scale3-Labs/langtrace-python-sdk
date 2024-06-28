import cohere
from dotenv import find_dotenv, load_dotenv

from langtrace_python_sdk import langtrace

_ = load_dotenv(find_dotenv())

langtrace.init()


co = cohere.Client()


# @with_langtrace_root_span("chat_stream")
def chat_stream():
    result = []
    for event in co.chat_stream(
        message="Tell me a short story in 2 lines",
        preamble="Respond like a pirate",
        max_tokens=100,
        k=3,
        p=0.9,
        temperature=0.5,
    ):
        if event.event_type == "text-generation":
            result.append(event.text)
        elif event.event_type == "stream-end":
            break
    print("".join(result))
    return result
