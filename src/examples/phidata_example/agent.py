from langtrace_python_sdk import langtrace
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo

langtrace.init()

def agent_run():
    web_agent = Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[DuckDuckGo()],
        instructions=["Always include sources"],
        show_tool_calls=True,
        markdown=True,
    )
    web_agent.print_response("how do I get from lagos to nairobi, through kigali rwanda (staying a week) and how much would it cost on average?", stream=True)
