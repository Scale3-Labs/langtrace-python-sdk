from langtrace_python_sdk import langtrace
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()

langtrace.init()

client = Cerebras()


def completion_example():
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Why is fast inference important?",
            }
        ],
        model="llama3.1-8b",
    )
    return completion
