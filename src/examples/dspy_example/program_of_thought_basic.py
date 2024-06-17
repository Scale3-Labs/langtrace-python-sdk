import dspy

# flake8: noqa
from langtrace_python_sdk import langtrace, with_langtrace_root_span

langtrace.init()

turbo = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=250)
dspy.settings.configure(lm=turbo)


# Define a simple signature for basic question answering
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""

    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


@with_langtrace_root_span(name="pot_example")
def example():

    # Pass signature to ProgramOfThought Module
    pot = dspy.ProgramOfThought(BasicQA)

    # Call the ProgramOfThought module on a particular input
    question = "Sarah has 5 apples. She buys 7 more apples from the store. How many apples does Sarah have now?"
    result = pot(question=question)

    print(f"Question: {question}")
    print(f"Final Predicted Answer (after ProgramOfThought process): {result.answer}")


if __name__ == "__main__":
    example()
