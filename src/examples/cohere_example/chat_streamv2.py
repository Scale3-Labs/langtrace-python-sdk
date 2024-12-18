import os
from langtrace_python_sdk import langtrace
import cohere

langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

def chat_stream_v2():
    res = co.chat_stream(
        model="command-r-plus-08-2024",
        messages=[{"role": "user", "content": "Write a title for a blog post about API design. Only output the title text"}],
    )

    for event in res:
        if event:
            if event.type == "content-delta":
                print(event.delta.message.content.text)