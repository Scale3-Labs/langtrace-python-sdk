from langtrace_python_sdk import langtrace
from autogen import ConversableAgent
from dotenv import load_dotenv
from autogen.coding import LocalCommandLineCodeExecutor
import tempfile


load_dotenv()
langtrace.init(write_spans_to_console=False)
# agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))
# Create a temporary directory to store the code files.
temp_dir = tempfile.TemporaryDirectory()


# Create a local command line code executor.
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)


def main():

    agent = ConversableAgent(
        "chatbot",
        llm_config={"config_list": [{"model": "gpt-4"}], "cache_seed": None},
        code_execution_config=False,  # Turn off code execution, by default it is off.
        function_map=None,  # No registered functions, by default it is None.
        human_input_mode="NEVER",  # Never ask for human input.
    )

    reply = agent.generate_reply(
        messages=[{"content": "Tell me a joke.", "role": "user"}]
    )
    return reply


def comedy_show():
    cathy = ConversableAgent(
        name="cathy",
        system_message="Your name is Cathy and you are a part of a duo of comedians.",
        llm_config={
            "config_list": [{"model": "gpt-4o-mini", "temperature": 0.9}],
            "cache_seed": None,
        },
        description="Cathy is a comedian",
        max_consecutive_auto_reply=10,
        code_execution_config={
            "executor": executor
        },  # Use the local command line code executor.
        function_map=None,
        chat_messages=None,
        silent=True,
        default_auto_reply="Sorry, I don't know what to say.",
        human_input_mode="NEVER",  # Never ask for human input.
    )

    joe = ConversableAgent(
        "joe",
        system_message="Your name is Joe and you are a part of a duo of comedians.",
        llm_config={
            "config_list": [{"model": "gpt-4o-mini", "temperature": 0.7}],
            "cache_seed": None,
        },
        human_input_mode="NEVER",  # Never ask for human input.
    )

    result = joe.initiate_chat(
        recipient=cathy, message="Cathy, tell me a joke.", max_turns=2
    )

    return result
