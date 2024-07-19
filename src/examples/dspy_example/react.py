import sys
import os
import dspy

# Add the local src folder to the Python path
sys.path.insert(
    0,
    os.path.abspath(
        "/Users/karthikkalyanaraman/work/langtrace/langtrace-python-sdk/src"
    ),
)

# flake8: noqa
from langtrace_python_sdk import langtrace, with_langtrace_root_span

langtrace.init()

turbo = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=250)
dspy.settings.configure(lm=turbo)

colbertv2_wiki17_abstracts = dspy.ColBERTv2(
    url="http://20.102.90.50:2017/wiki17_abstracts"
)
dspy.settings.configure(rm=colbertv2_wiki17_abstracts)
retriever = dspy.Retrieve(k=3)


# Define a simple signature for basic question answering
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""

    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


@with_langtrace_root_span(name="react_example")
def example():

    # Pass signature to ReAct module
    react_module = dspy.ReAct(BasicQA)

    # Call the ReAct module on a particular input
    question = "Aside from the Apple Remote, what other devices can control the program Apple Remote was originally designed to interact with?"
    result = react_module(question=question)

    print(f"Question: {question}")
    print(f"Final Predicted Answer (after ReAct process): {result.answer}")


if __name__ == "__main__":
    example()
