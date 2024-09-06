from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel
from typing_extensions import TypedDict
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, ToolMessage

from langtrace_python_sdk import langtrace

langtrace.init()

primes = {998: 7901, 999: 7907, 1000: 7919}


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


class State(TypedDict):
    messages: Annotated[list, add_messages]
    # This flag is new
    ask_human: bool


class RequestAssistance(BaseModel):
    """Escalate the conversation to an expert. Use this if you are unable to assist directly or if the user requires support beyond your permissions.

    To use this function, relay the user's 'request' so the expert can provide the right guidance.
    """

    request: str


llm = ChatAnthropic(model="claude-3-haiku-20240307")
# We can bind the llm to a tool definition, a pydantic model, or a json schema
llm_with_tools = llm.bind_tools([RequestAssistance])
tools = [
    Tool(
        name="GetPrime",
        func=get_prime,
        description="A tool that returns the `n`th prime number",
        args_schema=PrimeInput,
        coroutine=aget_prime,
    ),
]


def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    ask_human = False
    if (
        response.tool_calls
        and response.tool_calls[0]["name"] == RequestAssistance.__name__
    ):
        ask_human = True
    return {"messages": [response], "ask_human": ask_human}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))


def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )


def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # If they choose not to, we will include a placeholder ToolMessage to
        # let the LLM continue.
        new_messages.append(
            create_response("No response from human.", state["messages"][-1])
        )
    return {
        # Append the new messages
        "messages": new_messages,
        # Unset the flag
        "ask_human": False,
    }


def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    # Otherwise, we can route as before
    return tools_condition(state)


def basic_graph_tools():
    graph_builder.add_node("human", human_node)
    graph_builder.add_conditional_edges(
        "chatbot",
        select_next_node,
        {"human": "human", "tools": "tools", "__end__": "__end__"},
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("human", "chatbot")
    graph_builder.set_entry_point("chatbot")
    memory = MemorySaver()
    graph = graph_builder.compile(
        checkpointer=memory,
        interrupt_before=["human"],
    )

    config = {"configurable": {"thread_id": "1"}}
    events = graph.stream(
        {
            "messages": [
                (
                    "user",
                    "I'm learning LangGraph. Could you do some research on it for me?",
                )
            ]
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1]
