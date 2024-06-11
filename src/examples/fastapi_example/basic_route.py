from fastapi import FastAPI
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI

from langtrace_python_sdk import langtrace
from dotenv import load_dotenv

load_dotenv()
langtrace.init(write_spans_to_console=True)
app = FastAPI()
client = OpenAI()


@app.get("/")
def root():
    vectorstore = FAISS.from_texts(
        ["Langtrace helps you ship high quality AI Apps to production."],
        embedding=OpenAIEmbeddings(),
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

    res = chain.invoke("How is Langtrace useful?")
    return {"response": res}
