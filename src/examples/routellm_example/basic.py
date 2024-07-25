import sys

sys.path.insert(0, "/Users/karthikkalyanaraman/work/langtrace/langtrace-python-sdk/src")

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from routellm.controller import Controller
from dotenv import load_dotenv

load_dotenv()

langtrace.init()

# litellm.set_verbose=True
client = Controller(
    routers=["mf"],
    strong_model="claude-3-opus-20240229",
    weak_model="claude-3-opus-20240229",
)


@with_langtrace_root_span("Routellm")
def Routellm(prompt):
    try:

        response = client.chat.completions.create(
            model="router-mf-0.11593", messages=[{"role": "user", "content": prompt}]
        )

        for chunk in response:
            if hasattr(chunk, "choices"):
                print(chunk.choices[0].delta.content or "", end="")
            else:
                print(chunk)

    except Exception as e:
        print(f"An error occurred: {e}")


Routellm("what is the square root of 12182382932.99")
Routellm("Write me a short story")
