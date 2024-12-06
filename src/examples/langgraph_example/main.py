from typing import TypedDict, Union, Annotated
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.tools import tool
import operator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langchain import hub
from langchain.agents import create_openai_tools_agent
import json
from langgraph.graph import StateGraph, END
from langtrace_python_sdk import langtrace, with_langtrace_root_span

load_dotenv()

langtrace.init(write_spans_to_console=False)


class AgentState(TypedDict):
    input: str
    agent_out: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


ehi_information = """Title: EHI: End-to-end Learning of Hierarchical Index for
Efficient Dense Retrieval
Summary: Dense embedding-based retrieval is now the industry
standard for semantic search and ranking problems, like obtaining relevant web
documents for a given query. Such techniques use a two-stage process: (a)
contrastive learning to train a dual encoder to embed both the query and
documents and (b) approximate nearest neighbor search (ANNS) for finding similar
documents for a given query. These two stages are disjoint; the learned
embeddings might be ill-suited for the ANNS method and vice-versa, leading to
suboptimal performance. In this work, we propose End-to-end Hierarchical
Indexing -- EHI -- that jointly learns both the embeddings and the ANNS
structure to optimize retrieval performance. EHI uses a standard dual encoder
model for embedding queries and documents while learning an inverted file index
(IVF) style tree structure for efficient ANNS. To ensure stable and efficient
learning of discrete tree-based ANNS structure, EHI introduces the notion of
dense path embedding that captures the position of a query/document in the tree.
We demonstrate the effectiveness of EHI on several benchmarks, including
de-facto industry standard MS MARCO (Dev set and TREC DL19) datasets. For
example, with the same compute budget, EHI outperforms state-of-the-art (SOTA)
in by 0.6% (MRR@10) on MS MARCO dev set and by 4.2% (nDCG@10) on TREC DL19
benchmarks.
Author(s): Ramnath Kumar, Anshul Mittal, Nilesh Gupta, Aditya Kusupati,
Inderjit Dhillon, Prateek Jain
Source: https://arxiv.org/pdf/2310.08891.pdf"""


@tool("search")
def search_tool(query: str):
    """Searches for information on the topic of artificial intelligence (AI).
    Cannot be used to research any other topics. Search query must be provided
    in natural language and be verbose."""
    # this is a "RAG" emulator
    return ehi_information


@tool("final_answer")
def final_answer_tool(answer: str, source: str):
    """Returns a natural language response to the user in `answer`, and a
    `source` which provides citations for where this information came from.
    """
    return ""


llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")


query_agent_runnable = create_openai_tools_agent(
    llm=llm, tools=[final_answer_tool, search_tool], prompt=prompt
)


inputs = {"input": "what are EHI embeddings?", "intermediate_steps": []}

agent_out = query_agent_runnable.invoke(inputs)


def run_query_agent(state: list):
    print("> run_query_agent")
    agent_out = query_agent_runnable.invoke(state)
    return {"agent_out": agent_out}


def execute_search(state: list):
    print("> execute_search")
    action = state["agent_out"]
    tool_call = action[-1].message_log[-1].additional_kwargs["tool_calls"][-1]
    out = search_tool.invoke(json.loads(tool_call["function"]["arguments"]))
    return {"intermediate_steps": [{"search": str(out)}]}


def router(state: list):
    print("> router")
    if isinstance(state["agent_out"], list):
        return state["agent_out"][-1].tool
    else:
        return "error"


# finally, we will have a single LLM call that MUST use the final_answer structure
final_answer_llm = llm.bind_tools([final_answer_tool], tool_choice="final_answer")


# this forced final_answer LLM call will be used to structure output from our
# RAG endpoint
def rag_final_answer(state: list):
    print("> final_answer")
    query = state["input"]
    context = state["intermediate_steps"][-1]

    prompt = f"""You are a helpful assistant, answer the user's question using the
    context provided.

    CONTEXT: {context}

    QUESTION: {query}
    """
    out = final_answer_llm.invoke(prompt)
    function_call = out.additional_kwargs["tool_calls"][-1]["function"]["arguments"]
    return {"agent_out": function_call}


# we use the same forced final_answer LLM call to handle incorrectly formatted
# output from our query_agent
def handle_error(state: list):
    print("> handle_error")
    query = state["input"]
    prompt = f"""You are a helpful assistant, answer the user's question.

    QUESTION: {query}
    """
    out = final_answer_llm.invoke(prompt)
    function_call = out.additional_kwargs["tool_calls"][-1]["function"]["arguments"]
    return {"agent_out": function_call}


@with_langtrace_root_span("run_graph")
def run_graph():
    graph = StateGraph(AgentState)

    # we have four nodes that will consume our agent state and modify
    # our agent state based on some internal process
    graph.add_node("query_agent", run_query_agent)
    graph.add_node("search", execute_search)
    graph.add_node("error", handle_error)
    graph.add_node("rag_final_answer", rag_final_answer)
    # our graph will always begin with the query agent
    graph.set_entry_point("query_agent")
    # conditional edges are controlled by our router
    graph.add_conditional_edges(
        "query_agent",
        router,
        {
            "search": "search",
            "error": "error",
            "final_answer": END,
        },
    )
    graph.add_edge("search", "rag_final_answer")
    graph.add_edge("error", END)
    graph.add_edge("rag_final_answer", END)

    runnable = graph.compile()

    return runnable.invoke({"input": "what are EHI embeddings?"})


if __name__ == "__main__":
    run_graph()
