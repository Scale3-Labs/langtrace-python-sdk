from agents import PoetryAgents
from crewai import Crew
from dotenv import load_dotenv
from tasks import PoetryTasks

from langtrace_python_sdk import langtrace

load_dotenv()
langtrace.init()


class PoetryCrew:
    def __init__(self, topic) -> None:
        self.topic = topic

    def run(self):
        agents = PoetryAgents()
        tasks = PoetryTasks()

        poetry_agent = agents.create_poet_agent()
        # poetry_agent_2 = agents.poet_agent_2()
        # poetry_agent_3 = agents.poet_agent_3()

        create_poem = tasks.create_poem(poetry_agent, self.topic)
        # create_poem_2 = tasks.create_poem(poetry_agent_2, self.topic)
        # create_poem_3 = tasks.create_poem(poetry_agent_3, self.topic)

        crew = Crew(agents=[poetry_agent], tasks=[create_poem], verbose=True, memory=True)
        res = crew.kickoff()
        return res


# This is the main function that you will use to run your custom crew.
# You can run this file using `python -m src.examples.crewai_example.simple_agent.main`
if __name__ == "__main__":
    print("## Welcome to Poetry Crew")
    print("-------------------------------")
    poetry_crew = PoetryCrew(topic="cold")
    result = poetry_crew.run()
    print("\n\n########################")
    print("## Here is you poem")
    print("########################\n")
    print(result)
