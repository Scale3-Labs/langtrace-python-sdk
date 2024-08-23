import asyncio
from langtrace_python_sdk import langtrace
from mistralai import Mistral
import os

langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

async def main():
    s = Mistral(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
    )
    res = await s.chat.complete_async(model="mistral-small-latest", messages=[
        {
            "content": "Which locations should I visit when I travel to New york? Answer in one short sentence.",
            "role": "user",
        },
    ])
    if res is not None:
        # handle response
        print(res.choices[0].message.content)
        pass

asyncio.run(main())
print("hello")