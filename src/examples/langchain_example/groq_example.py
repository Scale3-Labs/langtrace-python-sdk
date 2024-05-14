from dotenv import find_dotenv, load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

_ = load_dotenv(find_dotenv())

from langtrace_python_sdk import langtrace

# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()


def groq_example():

    chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

    system = "You are a helpful assistant."
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    chain = prompt | chat
    result = chain.invoke(
        {"text": "Explain the importance of low latency LLMs in 2 sentences or less."}
    )
    # print(result)
    return result


groq_example()
