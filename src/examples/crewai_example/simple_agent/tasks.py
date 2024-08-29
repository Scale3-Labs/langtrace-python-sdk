from crewai import Task
from textwrap import dedent


class PoetryTasks:
    def create_poem(self, agent, topic):
        return Task(
            description=dedent(
                f"""
            **Task**: Create a Poem on {topic}
            **Description**: Write a poem on the given topic that captures the essence of the theme or emotion. 
                The poem should be creative, expressive, and resonate with the reader's emotions and experiences. 
                Your poem should be well-structured, engaging, and evoke a sense of beauty and meaning.

            **Parameters**: 
            - Topic: {topic}
        """
            ),
            expected_output="A creative and expressive poem that captures the essence of the given topic.",
            agent=agent,
            output_file="poem.txt",
        )
