from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from examples.openai.setup import setup_instrumentation

_ = load_dotenv(find_dotenv())

setup_instrumentation()

client = OpenAI()
def chat_completion():
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=True,
    )
    # stream = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": "Say this is a test three times"}, {"role": "assistant", "content": "This is a test. This is a test. This is a test"},
    #             {"role": "user", "content": "Say this is a mock 4 times"}],
    #     stream=True,
    # )