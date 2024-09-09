from langtrace_python_sdk import langtrace
from .async_tool_calling_streaming import (
    run_conversation as arun_conversation_streaming,
)
from .async_tool_calling_nonstreaming import (
    run_conversation as arun_conversation_nonstreaming,
)
from .chat_completion_tool_choice import (
    run_conversation as run_conversation_tool_choice,
)
from .chat_completion import chat_completion
from .embeddings_create import embeddings_create
from .function_calling import function_calling
from .images_edit import image_edit
from .images_generate import images_generate
from .tool_calling import tool_calling
from .tool_calling_nonstreaming import run_conversation as run_conversation_nonstreaming
from .tool_calling_streaming import run_conversation as run_conversation_streaming

from dotenv import load_dotenv
import asyncio

load_dotenv()
langtrace.init(write_spans_to_console=False, batch=False)


def run_main():
    # asyncio.run(arun_conversation_streaming())
    # asyncio.run(arun_conversation_nonstreaming())
    chat_completion(stream=True)
    chat_completion(stream=False)

    # embeddings_create()
    # function_calling()
    # image_edit()
    # images_generate()
    # tool_calling()
    # run_conversation_nonstreaming()
    # run_conversation_streaming()
    # run_conversation_tool_choice()
