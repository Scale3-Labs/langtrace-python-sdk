from dotenv import find_dotenv, load_dotenv
import cohere

from langtrace_python_sdk import langtrace
# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=False, debug_log_to_console=True, write_to_langtrace_cloud=False)

co = cohere.Client('bGFkbVRVgNGI0T4Y24AVo6F6sR8KsMej4vYHOmdz')


# @with_langtrace_root_span("chat_create")
def chat_comp():
    response = co.chat(
        chat_history=[
            {"role": "USER", "message": "Who discovered gravity?"},
            {"role": "CHATBOT", "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton"}
        ],
        message="What is today's news?",
        # preamble="answer like yoda",
        # perform web search before answering the question. You can also use your own custom connector.
        # connectors=[{"id": "web-search"}]
    )
    print(response)
