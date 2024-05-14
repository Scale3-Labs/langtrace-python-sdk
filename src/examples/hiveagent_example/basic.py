from langtrace_python_sdk import langtrace
from hive_agent import HiveAgent
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

langtrace.init(
    write_spans_to_console=True,
    api_host="http://localhost:3000",
)

client = OpenAI()


def basic():
    my_agent = HiveAgent(
        name="my_agent",
        functions=[],
        instruction="your instructions for this agent's goal",
    )

    my_agent.run_server()
