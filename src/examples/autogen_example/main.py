from langtrace_python_sdk import langtrace
import os
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from dotenv import load_dotenv
import agentops


load_dotenv()
langtrace.init(write_spans_to_console=False)
agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))


def main():

    agent = ConversableAgent(
        "chatbot",
        llm_config={"config_list": [{"model": "gpt-4"}]},
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
        "cathy",
        system_message="Your name is Cathy and you are a part of a duo of comedians.",
        llm_config={"config_list": [{"model": "gpt-4", "temperature": 0.9}]},
        human_input_mode="NEVER",  # Never ask for human input.
    )

    joe = ConversableAgent(
        "joe",
        system_message="Your name is Joe and you are a part of a duo of comedians.",
        llm_config={"config_list": [{"model": "gpt-4", "temperature": 0.7}]},
        human_input_mode="NEVER",  # Never ask for human input.
    )

    result = joe.initiate_chat(
        recipient=cathy, message="Cathy, tell me a joke.", max_turns=2
    )

    return result
