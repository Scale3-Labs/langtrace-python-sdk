from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_cohere import ChatCohere
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()


class TravelAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        self.OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        self.Ollama = ChatOllama(model="llama3")
        self.Cohere = ChatCohere(model="command-r")
        self.Anthropic = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    def expert_travel_agent(self):
        return Agent(
            role="Expert Travel Agent",
            backstory="""
                    I am an Expert in travel planning and itinerary creation.
                    I have been in the travel industry for over 10 years and have helped thousands of clients plan their dream vacations.
                    I have extensive knowledge of popular travel destinations, local attractions, and travel logistics. I am here to help you create a personalized travel itinerary that suits your preferences and budget.
                """,
            goal="""Create a 7 day travel itinerary with detailed per-day plans, include budget, packing suggestions, and local/safety tips.""",
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.Cohere,
        )

    def city_selection_expert(self):
        return Agent(
            role="City Selection Expert",
            backstory="""Expert at analyzing and selecting the best cities for travel based on data""",
            goal="""Select the best cities based on weather, season, prices and traveler preferences""",
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.Cohere,
        )

    def local_tour_guide(self):
        return Agent(
            role="Local Expert at this city",
            goal="Provide the BEST insights about the selected city",
            backstory="""A knowledgeable local guide with extensive information about the city, it's attractions and customs""",
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.Cohere,
        )
