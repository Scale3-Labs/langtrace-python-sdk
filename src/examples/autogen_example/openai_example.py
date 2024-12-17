import os
import autogen
from langtrace_python_sdk import langtrace

# Initialize Langtrace
langtrace.init(
    api_key='967b06c4d1858a7e64e58de44708d89e84f8c96a69b20f7276bcb34a7ce495af',
    api_host="http://localhost:3000/api/trace"
)

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "sk-proj-dv2lt1rbQKs3qUL0Yp6VT3BlbkFJ36T4v1wH0tNmhkjQiXSe"

# Configure OpenAI for autogen
config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": os.environ["OPENAI_API_KEY"]
    }
]

# Create assistant and user agents
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list},
    system_message="You are a helpful AI assistant."
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    llm_config={"config_list": config_list},
)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message="Write a Python function to calculate the first n terms of the Fibonacci sequence."
)
