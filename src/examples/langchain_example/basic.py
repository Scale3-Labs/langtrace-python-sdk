from dotenv import find_dotenv, load_dotenv
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from instrumentation.setup import setup_instrumentation
from instrumentation.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

setup_instrumentation()


# @with_langtrace_root_span()
def basic():
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are world class technical documentation writer."),
        ("user", "{input}")
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    res = chain.invoke({"input": "how can langsmith help with testing?"})
    print(res)


@with_langtrace_root_span()
def rag():
    vectorstore = FAISS.from_texts(
        ["harrison worked at kensho"], embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()

    template = """Answer the question based only on the following context:{context}

        Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    model = ChatOpenAI()

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    res = chain.invoke("where did harrison work?")
    # print(res)
