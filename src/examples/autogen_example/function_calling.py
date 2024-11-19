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

# Define a function that the agent can call
def calculate_square(x: int) -> int:
    """Calculate the square of a number."""
    return x * x

# Configure the agent
config_list = [{"model": "gpt-3.5-turbo", "api_key": os.getenv("OPENAI_API_KEY")}]
llm_config = {
    "config_list": config_list,
    "seed": 42,
    "functions": [
        {
            "name": "calculate_square",
            "description": "Calculate the square of a number",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "The number to square"
                    }
                },
                "required": ["x"]
            }
        }
    ]
}

# Create the assistant
assistant = autogen.AssistantAgent(
    name="math_assistant",
    system_message="You are a math assistant. Use the calculate_square function when asked about squaring numbers.",
    llm_config=llm_config,
    function_map={"calculate_square": calculate_square}
)

# Create the user proxy
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    llm_config=llm_config,
)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message="What is the square of 7?",
)
