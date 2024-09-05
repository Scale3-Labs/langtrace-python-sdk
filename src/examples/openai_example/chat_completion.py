from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

client = OpenAI()


def api():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Talk like a pirate"},
            {"role": "user", "content": "Tell me a story in 3 sentences or less."},
        ],
        # stream=True,
        # stream_options={"include_usage": True},
        stream=False,
    )
    return response


def chat_completion():
    response = api()
    # print(response)
    # Uncomment this for streaming
    # result = []
    # for chunk in response:
    #     if chunk.choices and chunk.choices[0].delta.content is not None:
    #         content = [
    #             choice.delta.content if choice.delta and choice.delta.content else ""
    #             for choice in chunk.choices
    #         ]
    #         result.append(content[0] if len(content) > 0 else "")

    # # print("".join(result))
    return response
