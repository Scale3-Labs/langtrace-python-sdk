from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from dotenv import find_dotenv, load_dotenv
from langtrace_python_sdk import langtrace

_ = load_dotenv(find_dotenv())

langtrace.init()

@with_langtrace_root_span("basic_google_genai")
def basic_google_genai():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    # example
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "What's in this image?",
            },
        ]
    )
    message_image = HumanMessage(content="https://picsum.photos/seed/picsum/200/300")

    res = llm.invoke([message, message_image])
    # print(res)


basic_google_genai()
