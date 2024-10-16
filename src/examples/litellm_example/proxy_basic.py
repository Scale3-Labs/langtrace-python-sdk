import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(base_url="http://0.0.0.0:4000")

# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "this is a test request, write a short poem"}
    ],
)

print(response)
