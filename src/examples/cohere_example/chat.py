from dotenv import find_dotenv, load_dotenv
import cohere

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=False, debug_log_to_console=True, write_to_langtrace_cloud=False)

co = cohere.Client()


@with_langtrace_root_span("chat_create")
def chat_comp():
        chat = co.chat(
        message="Say this is a test three times",
        model="command"
    )