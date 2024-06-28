import cohere
from dotenv import find_dotenv, load_dotenv

from langtrace_python_sdk import langtrace

# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()


co = cohere.Client()


# @with_langtrace_root_span("chat_create")
def chat_comp():
    response = co.chat(
        chat_history=[
            {"role": "USER", "message": "Who discovered gravity?"},
            {
                "role": "CHATBOT",
                "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton",
            },
        ],
        k=3,
        message="Tell me a story in 3 sentences or less?",
        preamble="answer like a pirate",
        # perform web search before answering the question. You can also use your own custom connector.
        connectors=[{"id": "web-search"}],
    )
    print(response)
