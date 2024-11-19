import os
from dotenv import load_dotenv
import autogen
from langtrace_python_sdk import langtrace

# Load environment variables
load_dotenv()

# Initialize langtrace
langtrace.init(
    api_key="2489f432edfcf4d7e90cbd20cdd1f35ba0654d7b106852c8bedebcecb8f23e05",
    write_spans_to_console=True,
)

# Configure agents
config_list = [{"model": "gpt-3.5-turbo", "api_key": os.getenv("OPENAI_API_KEY")}]
llm_config = {"config_list": config_list, "seed": 42}

# Create agents
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="A human user who needs help with coding tasks.",
    llm_config=llm_config,
)

coder = autogen.AssistantAgent(
    name="Coder",
    system_message="A senior Python developer who writes clean, efficient code.",
    llm_config=llm_config,
)

reviewer = autogen.AssistantAgent(
    name="Reviewer",
    system_message="A code reviewer who ensures code quality and suggests improvements.",
    llm_config=llm_config,
)

# Create group chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, coder, reviewer],
    messages=[],
    max_round=5
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Start the chat
user_proxy.initiate_chat(
    manager,
    message="Write a Python function to calculate the Fibonacci sequence up to n terms.",
)
