import os
from langtrace_python_sdk import with_langtrace_root_span
from mistralai import Mistral

@with_langtrace_root_span("chat_complete")
def chat_complete():
    model = "mistral-large-latest"
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
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
