"""Example of using the anthropic API to create a message."""

import anthropic
from dotenv import find_dotenv, load_dotenv

from langtrace_python_sdk import langtrace, with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()


@with_langtrace_root_span("messages_create")
def messages_create():
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.0,
        system="Respond only in Yoda-speak.",
        messages=[{"role": "user", "content": "How are you today?"}],
        stream=True,
    )

    # print(message)

    for response in message:
        pass
