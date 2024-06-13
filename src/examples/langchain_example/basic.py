from dotenv import find_dotenv, load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from openai import OpenAI

_ = load_dotenv(find_dotenv())

langtrace.init(
    write_spans_to_console=False,
    disable_tracing_for_functions={"langchain": ["RunnableSequence.invoke"]},
)


def api_call_1():
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are world class technical documentation writer."),
            ("user", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    res = chain.invoke({"input": "how can langsmith help with testing?"})
    # print(res)
    return res


def api_call_2():
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are world class technical documentation writer."),
            ("user", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    res = chain.invoke({"input": "how can langsmith help with testing?"})
    # print(res)
    return res


@with_langtrace_root_span()
def basic_app():
    api_call_1()
    # api_call_2()
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Talk like a pirate"},
            {"role": "user", "content": "Tell me a story in 3 sentences or less."},
        ],
        # stream=True,
        stream=False,
    )

    return response


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


@with_langtrace_root_span()
def load_and_split():
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    loader = PyPDFLoader(url)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    docs = text_splitter.split_documents(data)
    # print(docs)
