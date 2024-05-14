import json

from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessageGraph

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init()


@tool
def multiply(first_number: int, second_number: int):
    """Multiplies two numbers together."""
    return first_number * second_number


model = ChatOpenAI(temperature=0)
model_with_tools = model.bind(tools=[convert_to_openai_tool(multiply)])


def invoke_model(state):
    return model_with_tools.invoke(state)


def router(state):
    tool_calls = state[-1].additional_kwargs.get("tool_calls", [])
    if len(tool_calls):
        return "multiply"
    else:
        return "end"


def invoke_tool(state):
    tool_calls = state[-1].additional_kwargs.get("tool_calls", [])
    multiply_call = None

    for tool_call in tool_calls:
        if tool_call.get("function").get("name") == "multiply":
            multiply_call = tool_call

    if multiply_call is None:
        raise Exception("No adder input found.")

    res = multiply.invoke(json.loads(multiply_call.get("function").get("arguments")))

    return ToolMessage(tool_call_id=multiply_call.get("id"), content=res)


@with_langtrace_root_span("langgraph_example")
def basic():

    graph = MessageGraph()

    graph.add_node("oracle", invoke_model)

    graph.add_node("multiply", invoke_tool)

    graph.add_conditional_edges(
        "oracle",
        router,
        {
            "multiply": "multiply",
            "end": END,
        },
    )

    graph.add_edge("multiply", END)

    graph.set_entry_point("oracle")

    runnable = graph.compile()

    answer = runnable.invoke(HumanMessage("What is 1 + 1?"))
    print(answer)


basic()
