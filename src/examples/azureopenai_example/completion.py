import os
from langchain_openai import AzureChatOpenAI

from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

model = AzureChatOpenAI(
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
    azure_deployment=os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'],
    openai_api_version=os.environ['AZURE_OPENAI_API_VERSION'],
)

@with_langtrace_root_span()
def chat_completion():
    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]
    result = model.invoke(messages)
    print(result)
