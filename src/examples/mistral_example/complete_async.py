from dotenv import find_dotenv, load_dotenv
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from mistralai import Mistral

_ = load_dotenv(find_dotenv())

langtrace.init()

@with_langtrace_root_span("chat_complete_async")
async def complete_async():
    client = Mistral()
    res = await client.chat.complete_async(model="mistral-small-latest", messages=[
        {
            "content": "Which locations should I visit when I travel to New york? Answer in one short sentence.",
            "role": "user",
        },
    ])
    if res is not None:
        # handle response
        print(res.choices[0].message.content)
