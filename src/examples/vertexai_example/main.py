import vertexai
import base64
import asyncio
import vertexai.preview.generative_models as generative_models
from vertexai.language_models import ChatModel, InputOutputTextPair, TextGenerationModel
from langtrace_python_sdk import langtrace
from vertexai.generative_models import GenerativeModel, Part, FinishReason
from dotenv import load_dotenv

load_dotenv()

langtrace.init()
vertexai.init(project="model-palace-429011-f5", location="us-central1")


def basic():
    # chat()
    # chat_streaming()
    # streaming_prediction()
    generate()
    # asyncio.run(async_streaming_prediction())


def chat():
    """Chat Example with a Large Language Model"""

    chat_model = ChatModel.from_pretrained("chat-bison")

    parameters = {
        "temperature": 0.8,
        "max_output_tokens": 256,
        "top_p": 0.95,
        "top_k": 40,
    }

    chat = chat_model.start_chat(
        context="My name is Miles. You are an astronomer, knowledgeable about the solar system.",
        examples=[
            InputOutputTextPair(
                input_text="How many moons does Mars have?",
                output_text="The planet Mars has two moons, Phobos and Deimos.",
            ),
        ],
    )

    response = chat.send_message(
        message="How many planets are there in the solar system?", **parameters
    )

    return response


def chat_streaming() -> str:
    """Streaming Chat Example with a Large Language Model"""

    chat_model = ChatModel.from_pretrained("chat-bison")

    parameters = {
        "temperature": 0.8,
        "max_output_tokens": 256,
        "top_p": 0.95,
        "top_k": 40,
    }

    chat = chat_model.start_chat(
        context="My name is Miles. You are an astronomer, knowledgeable about the solar system.",
        examples=[
            InputOutputTextPair(
                input_text="How many moons does Mars have?",
                output_text="The planet Mars has two moons, Phobos and Deimos.",
            ),
        ],
    )

    responses = chat.send_message_streaming(
        message="How many planets are there in the solar system?", **parameters
    )

    result = [response for response in responses]
    return result


def streaming_prediction() -> str:
    """Streaming Text Example with a Large Language Model"""

    text_generation_model = TextGenerationModel.from_pretrained("text-bison")
    parameters = {
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40,
    }
    responses = text_generation_model.predict_streaming(
        prompt="Give me ten interview questions for the role of program manager.",
        **parameters,
    )
    result = [response for response in responses]
    print(result)
    return result


async def async_streaming_prediction() -> str:
    """Async Streaming Text Example with a Large Language Model"""

    text_generation_model = TextGenerationModel.from_pretrained("text-bison")
    parameters = {
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40,
    }

    responses = text_generation_model.predict_streaming_async(
        prompt="Give me ten interview questions for the role of program manager.",
        **parameters,
    )

    result = [response async for response in responses]
    print(result)
    return result


def generate():
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
    }
    model = GenerativeModel(
        "gemini-experimental",
    )

    responses = model.generate_content(
        ["I am a software engineer. I enjoy playing video games and reading"],
        generation_config=generation_config,
        stream=True,
    )

    for response in responses:
        pass
