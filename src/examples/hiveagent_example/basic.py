# from langtrace_python_sdk import langtrace
from hive_agent import HiveAgent
from dotenv import load_dotenv
from langtrace_python_sdk.utils.agent import agent
from langtrace_python_sdk import langtrace
from openai import OpenAI
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

load_dotenv()

langtrace.init(
    debug_log_to_console=True,
    write_to_langtrace_cloud=False,
    batch=False,
    api_host="http://localhost:3000",
    api_key="d134ad619428e03476f1a42abf991d871a2a560a49a520e6331a4c3704228c78",
)

client = OpenAI()


def basic():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    # my_agent = HiveAgent(
    #     name="my_agent",
    #     functions=[],
    #     instruction="your instructions for this agent's goal",
    # )

    # my_agent.run_server()
