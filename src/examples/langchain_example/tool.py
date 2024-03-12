from dotenv import find_dotenv, load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.chains import LLMMathChain
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=True, log_spans_to_console=True,
               write_to_remote_url=False)


llm = ChatOpenAI(temperature=0, model="gpt-4")
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

primes = {998: 7901, 999: 7907, 1000: 7919}


class CalculatorInput(BaseModel):
    question: str = Field()


class PrimeInput(BaseModel):
    n: int = Field()


def is_prime(n: int) -> bool:
    if n <= 1 or (n % 2 == 0 and n > 2):
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def get_prime(n: int, primes: dict = primes) -> str:
    return str(primes.get(int(n)))


async def aget_prime(n: int, primes: dict = primes) -> str:
    return str(primes.get(int(n)))


@with_langtrace_root_span()
def tool_example():

    tools = [
        Tool(
            name="GetPrime",
            func=get_prime,
            description="A tool that returns the `n`th prime number",
            args_schema=PrimeInput,
            coroutine=aget_prime,
        ),
        Tool.from_function(
            func=llm_math_chain.run,
            name="Calculator",
            description="Useful for when you need to compute mathematical expressions",
            args_schema=CalculatorInput,
            coroutine=llm_math_chain.arun,
        ),
    ]

    prompt = hub.pull("hwchase17/openai-functions-agent")

    agent = create_openai_functions_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    question = "What is the product of the 998th, 999th and 1000th prime numbers?"

    for step in agent_executor.iter({"input": question}):
        if output := step.get("intermediate_step"):
            action, value = output[0]
            if action.tool == "GetPrime":
                print(f"Checking whether {value} is prime...")
                assert is_prime(int(value))
            # Ask user if they want to continue
            _continue = input("Should the agent continue (Y/n)?:\n") or "Y"
            if _continue.lower() != "y":
                break
