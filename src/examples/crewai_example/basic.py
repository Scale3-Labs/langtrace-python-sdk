import os

os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
os.environ["SERPER_API_KEY"] = ""  # serper.dev API key
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from crewai import Crew, Process
from crewai import Task
from crewai import Agent
from crewai_tools import SerperDevTool
from crewai_tools import YoutubeVideoSearchTool

langtrace.init()

search_tool = SerperDevTool()

# Targeted search within a specific Youtube video's content
youtube_tool = YoutubeVideoSearchTool(
    youtube_video_url="https://www.youtube.com/watch?v=blqIZGXWUpU"
)

# Creating a senior researcher agent with memory and verbose mode
researcher = Agent(
    role="Senior Researcher",
    goal="Uncover groundbreaking technologies in {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of"
        "innovation, eager to explore and share knowledge that could change"
        "the world."
    ),
    tools=[youtube_tool],
)

# Research task
research_task = Task(
    description=(
        "Do a {topic} of the given youtube video."
        "Focus on identifying the overall narrative."
        "Your final report should clearly articulate the key points."
    ),
    expected_output="10 key points from the shared video.",
    tools=[youtube_tool],
    agent=researcher,
    callback="research_callback",  # Example of task callback
    human_input=True,
)


# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    process=Process.sequential,  # Optional: Sequential task execution is default
    memory=False,
    cache=False,
    max_rpm=20,
)

# Starting the task execution process with enhanced feedback


@with_langtrace_root_span("Crew")
def test_crew():
    result = crew.kickoff(inputs={"topic": "summary"})
    return result


test_crew()
