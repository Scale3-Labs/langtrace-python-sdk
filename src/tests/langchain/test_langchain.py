import pytest
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


@pytest.mark.vcr()
def test_langchain(exporter):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are world class technical documentation writer."),
            ("user", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    chain.invoke({"input": "how can langsmith help with testing?"})
    spans = exporter.get_finished_spans()

    assert [
        "ChatPromptTemplate.invoke",
        "openai.chat.completions.create",
        "StrOutputParser.parse",
        "StrOutputParser.parse_result",
        "StrOutputParser.invoke",
        "RunnableSequence.invoke",
    ] == [span.name for span in spans]


def test_load_and_split(exporter):
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    loader = PyPDFLoader(url)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    text_splitter.split_documents(data)
    spans = exporter.get_finished_spans()
    assert [
        "PagedPDFSplitter.lazy_load",
        "PyPDFLoader.lazy_load",
        "BasePDFLoader.load",
        "PagedPDFSplitter.load",
        "PyPDFLoader.load",
    ] == [span.name for span in spans]
