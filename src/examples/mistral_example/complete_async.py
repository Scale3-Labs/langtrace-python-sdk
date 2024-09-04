import os
from langtrace_python_sdk import with_langtrace_root_span
from mistralai import Mistral

@with_langtrace_root_span("chat_complete_async")
async def complete_async():
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    res = await client.chat.complete_async(model="mistral-small-latest", messages=[
        {
            "content": "Which locations should I visit when I travel to New york? Answer in one short sentence.",
            "role": "user",
        },
    ])
    if res is not None:
        # handle response
        print(res.choices[0].message.content)
