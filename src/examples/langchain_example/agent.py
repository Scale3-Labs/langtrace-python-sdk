from langtrace_python_sdk import langtrace
import os
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
import asyncio
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_tool_calling_agent
from langchain import hub
from langchain.agents import AgentExecutor

load_dotenv()
langtrace.init(write_spans_to_console=False)

model = ChatOpenAI()

# initializing tavily

search = TavilySearchResults(max_results=2)

toolxs = [search]

model_with_tools = model.bind_tools(toolxs)

# Create a prompt template
prompt = hub.pull("hwchase17/openai-functions-agent")


agent = create_tool_calling_agent(model, toolxs, prompt)


agent_executor = AgentExecutor(agent=agent, tools=toolxs, verbose=True)


async def chat_interface():
    print("Welcome to the AI Chat Interface!")
    print("Type 'quit' to exit the chat.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            print("Thank you for chatting. Goodbye!")
            break

        print("AI: Thinking...")
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"AI: {result['output']}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(chat_interface())
