import pytest
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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
