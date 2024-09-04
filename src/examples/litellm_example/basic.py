from langtrace_python_sdk import with_langtrace_root_span, langtrace
from dotenv import load_dotenv
from litellm import completion, acompletion
import litellm
import asyncio

load_dotenv()


litellm.success_callback = ["langtrace"]
langtrace.init()
litellm.set_verbose = False


@with_langtrace_root_span("Litellm Example OpenAI")
def openAI(streaming=False):
    response = completion(
        model="gpt-3.5-turbo",
        messages=[
            {"content": "respond only in Yoda speak.", "role": "system"},
            {"content": "Hello, how are you?", "role": "user"},
        ],
        stream=streaming,
        stream_options={"include_usage": True},
    )
    if streaming:
        for _ in response:
            pass
    else:
        return response


# @with_langtrace_root_span("Litellm Example Anthropic Completion")
def anthropic(streaming=False):
    try:

        response = completion(
            model="claude-2.1",
            messages=[
                {"content": "respond only in Yoda speak.", "role": "system"},
                {"content": "what is 2 + 2?", "role": "user"},
            ],
            temperature=0.5,
            top_p=0.5,
            n=1,
            stream=streaming,
            stream_options={"include_usage": True},
        )
        # print(response)
        if streaming:
            for _ in response:
                pass
        else:
            return response
    except Exception as e:
        print("ERORRRR", e)


# @with_langtrace_root_span("Litellm Example OpenAI Async Streaming")
async def async_anthropic(streaming=False):
    response = await acompletion(
        model="claude-2.1",
        messages=[{"content": "Hello, how are you?", "role": "user"}],
        stream=streaming,
        stream_options={"include_usage": True},
        temperature=0.5,
        top_p=0.5,
        n=1,
    )
    if streaming:
        async for _ in response:
            pass
    else:
        return response


def cohere(streaming=False):
    response = completion(
        model="command-r",
        messages=[
            {"content": "respond only in Yoda speak.", "role": "system"},
            {"content": "Hello, how are you?", "role": "user"},
        ],
        stream=streaming,
        stream_options={"include_usage": True},
    )
    if streaming:
        for _ in response:
            pass
    else:
        return response


if __name__ == "__main__":
    # openAI()
    anthropic(streaming=False)
    cohere(streaming=True)
    # asyncio.run(async_anthropic(streaming=True))
