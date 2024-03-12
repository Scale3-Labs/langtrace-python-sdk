from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=False, log_spans_to_console=True,
               write_to_remote_url=False)

client = OpenAI()


@with_langtrace_root_span()
def chat_completion():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=True,
    )
    # print(stream)
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
