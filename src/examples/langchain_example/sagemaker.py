import json
from typing import Dict

import boto3
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms.sagemaker_endpoint import (LLMContentHandler,
                                                         SagemakerEndpoint)
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from langtrace_python_sdk import langtrace, with_langtrace_root_span

# Add the path to the root of the project to the sys.path

load_dotenv()

langtrace.init()
example_doc_1 = """
Peter and Elizabeth took a taxi to attend the night party in the city. While in the party, Elizabeth collapsed and was rushed to the hospital.
Since she was diagnosed with a brain injury, the doctor told Peter to stay besides her until she gets well.
Therefore, Peter stayed with her at the hospital for 3 days without leaving.
"""

docs = [
    Document(
        page_content=example_doc_1,
    )
]


query = """How long was Elizabeth hospitalized?"""
prompt_template = """Use the following pieces of context to answer the question at the end.

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


client = boto3.client(
    "sagemaker-runtime",
    region_name="us-east-1",
)


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["generated_text"]


@with_langtrace_root_span("SagemakerEndpoint")
def main():
    content_handler = ContentHandler()

    chain = load_qa_chain(
        llm=SagemakerEndpoint(
            endpoint_name="jumpstart-dft-meta-textgeneration-l-20240809-083223",
            client=client,
            model_kwargs={"temperature": 1e-10},
            content_handler=content_handler,
        ),
        prompt=PROMPT,
    )

    res = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
    print(res)


main()
