from crewai import Agent
from langchain_anthropic import ChatAnthropic
from langchain_cohere import ChatCohere
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


class PoetryAgents:
    def __init__(self):
        self.open_ai = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        self.anthropic = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620", temperature=0.7
        )

        self.cohere = ChatCohere(model="command-r", temperature=0.7)
        self.ollama = ChatOllama(model="llama3", temperature=0.7)

    def create_poet_agent(self):
        return Agent(
            role="Expert Poetry Writer",
            backstory="""
                    I am an Expert in poetry writing and creative expression.
                    I have been writing poetry for over 10 years and have published several collections.
                    I have a deep understanding of various poetic forms, styles, and themes. I am here to help you create beautiful and meaningful poetry that resonates with your emotions and experiences.
                """,
            goal="""Create a poem that captures the essence of a given theme or emotion""",
            allow_delegation=False,
            verbose=True,
            llm=self.open_ai,
        )
    
    def poet_agent_2(self):
        return Agent(
            role="Renaissance Poet",
            backstory="""
                    I am a Renaissance Poet. I am well-versed in the art of poetry and have a deep appreciation for the beauty of language and expression.
                """,
            goal="""Create a poem that is inspired by the works of the Renaissance poets""",
            allow_delegation=False,
            verbose=True,
            llm=self.open_ai,
        )

    def poet_agent_3(self):
        return Agent(
            role="William Shakespeare",
            backstory="""
                    I am william shakespeare. I am an Expert in poetry writing and creative expression.
                    I have been writing poetry for over 10 years and have published several collections.
                """,
            goal="""Create a poem that is inspired by the works of William Shakespeare""",
            allow_delegation=False,
            verbose=True,
            llm=self.open_ai,
        )
