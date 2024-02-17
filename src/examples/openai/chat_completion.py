import os
from openai import OpenAI
from examples.openai.setup import setup_instrumentation
client = OpenAI()
setup_instrumentation()
def chat_completion():
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}, {"role": "assistant", "content": "This is a test. This is a test. This is a test"},
                {"role": "user", "content": "Say this is a mock 4 times"}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")