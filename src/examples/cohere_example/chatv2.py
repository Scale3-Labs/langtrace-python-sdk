import os
from langtrace_python_sdk import langtrace
import cohere

langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))


def chat_v2():
    co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

    res = co.chat(
        model="command-r-plus-08-2024",
        messages=[
            {
                "role": "user",
                "content": "Write a title for a blog post about API design. Only output the title text.",
            }
        ],
    )

    print(res.message.content[0].text)
