from langtrace_python_sdk import langtrace
import google.generativeai as genai
from dotenv import load_dotenv
import os
import asyncio
import pathlib
from .function_tools import tools

load_dotenv()

langtrace.init(write_spans_to_console=False, batch=False)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


async def async_demo():
    task1 = asyncio.create_task(async_generate())
    task2 = asyncio.create_task(async_generate(stream=True))
    return await asyncio.gather(task1, task2)


def basic():
    generate()
    generate(stream=True, with_tools=True)

    # image_to_text()
    # audio_to_text()
    asyncio.run(async_demo())


def generate(stream=False, with_tools=False):
    model = genai.GenerativeModel(
        "gemini-1.5-pro", system_instruction="You are a cat. Your name is Neko."
    )

    response = model.generate_content(
        "Write a story about a AI and magic",
        stream=stream,
        tools=tools if with_tools else None,
    )
    if stream:
        for res in response:
            if res.text:
                print(res.text)
    else:
        print(response.text)


async def async_generate(stream=False):
    model = genai.GenerativeModel(
        "gemini-1.5-pro", system_instruction="You are a cat. Your name is Neko."
    )
    response = await model.generate_content_async(
        "Write a story about a AI and magic", stream=stream
    )
    if stream:
        async for chunk in response:
            if chunk.text:
                print(chunk.text)
    else:
        print(response.text)


def image_to_text(stream=False):
    model = genai.GenerativeModel("gemini-1.5-flash")
    image1 = {
        "mime_type": "image/jpeg",
        "data": pathlib.Path("src/examples/gemini_example/jetpack.jpg").read_bytes(),
    }

    prompt = "Describe me this picture. What do you see in it."
    response = model.generate_content([prompt, image1], stream=stream)
    if stream:
        for res in response:
            print(res.text)
    else:
        print(response.text)


# def audio_to_text(stream=False):
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     audio = genai.upload_file(
#         pathlib.Path("src/examples/gemini_example/voice_note.mp3")
#     )

#     prompt = "Summarize this voice recording."
#     response = model.generate_content([prompt, audio], stream=stream)
#     if stream:
#         for res in response:
#             print(res.text)
#     else:
#         print(response.text)
