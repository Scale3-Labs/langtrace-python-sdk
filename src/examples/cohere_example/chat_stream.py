from dotenv import find_dotenv, load_dotenv
import cohere

from langtrace_python_sdk import langtrace
# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=False, debug_log_to_console=True, write_to_langtrace_cloud=False)

co = cohere.Client()


# @with_langtrace_root_span("chat_stream")
def chat_stream():
    result = []
    for event in co.chat_stream(message="Tell me a short story in 2 lines"):
        if event.event_type == "text-generation":
            result.append(event.text)
        elif event.event_type == "stream-end":
            break
    print("".join(result))
    return result
