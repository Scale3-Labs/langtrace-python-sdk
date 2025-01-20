from google import genai
from dotenv import load_dotenv
import os
from langtrace_python_sdk import langtrace

load_dotenv()
langtrace.init(write_spans_to_console=False)


def generate_content():
    # Only run this block for Google AI API
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents="What is your name?"
    )

    print(response.text)


def generate_content_streaming():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash-exp", contents="What is your name?"
    )

    for chunk in response:
        pass
