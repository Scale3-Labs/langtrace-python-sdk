from langtrace_python_sdk import with_langtrace_root_span, langtrace
from dotenv import load_dotenv
from litellm import completion, acompletion
import litellm

litellm.set_verbose = False
load_dotenv()
langtrace.init(write_spans_to_console=True)


@with_langtrace_root_span("Litellm Example OpenAI")
def openAI():
    response = completion(
        model="gpt-3.5-turbo",
        messages=[{"content": "Hello, how are you?", "role": "user"}],
    )
    return response


@with_langtrace_root_span("Litellm Example Anthropic Completion")
def anthropic():
    response = completion(
        model="claude-2",
        messages=[{"content": "Hello, how are you?", "role": "user"}],
        temperature=0.5,
        top_p=0.5,
        n=1,
    )
    print(response)
    return response


@with_langtrace_root_span("Litellm Example Anthropic Streaming")
def anthropic_streaming():
    response = completion(
        model="claude-2",
        messages=[{"content": "Hello, how are you?", "role": "user"}],
        stream=True,
        temperature=0.5,
        # presence_penalty=0.5,
        # frequency_penalty=0.5,
        top_p=0.5,
        n=1,
        # logit_bias={"Hello": 1.0},
        # top_logprobs=1,
    )
    for _ in response:
        pass

    return response


@with_langtrace_root_span("Litellm Example OpenAI Async Streaming")
async def async_anthropic_streaming():
    response = await acompletion(
        model="claude-2",
        messages=[{"content": "Hello, how are you?", "role": "user"}],
        stream=True,
        temperature=0.5,
        top_p=0.5,
        n=1,
    )
    async for _ in response:
        pass
