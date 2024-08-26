from dotenv import find_dotenv, load_dotenv
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from mistralai import Mistral

_ = load_dotenv(find_dotenv())

langtrace.init()

@with_langtrace_root_span("chat_complete")
def chat_complete():
    model = "mistral-large-latest"
    client = Mistral()
    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": "I need 10 cocktail recipes with tequila other than the classics like margarita, tequila"
            },
        ]
    )
    print(chat_response.choices[0].message.content)
