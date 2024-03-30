from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import (
    with_langtrace_root_span,
    with_additional_attributes,
)

_ = load_dotenv(find_dotenv())

langtrace.init()
client = OpenAI()


@with_additional_attributes({"user.id": "1234", "user.feedback.rating": 1})
def api1():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response


@with_additional_attributes({"user.id": "5678", "user.feedback.rating": -1})
def api2():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response


@with_langtrace_root_span()
def chat_completion():
    response = api1()
    response = api2()
    return response


# print(response)
# stream = client.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": "Say this is a test three times"}, {"role": "assistant", "content": "This is a test. This is a test. This is a test"},
#               {"role": "user", "content": "Say this is a mock 4 times"}],
#     stream=False,
# )

# result = []
# for chunk in response:
#     if chunk.choices[0].delta.content is not None:
#         content = [
#             choice.delta.content if choice.delta and
#             choice.delta.content else ""
#             for choice in chunk.choices]
#         result.append(
#             content[0] if len(content) > 0 else "")

# print("".join(result))
