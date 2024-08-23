import os
from langtrace_python_sdk import langtrace
from mistralai import Mistral

langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

def main():
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


if __name__ == "__main__":
    main()