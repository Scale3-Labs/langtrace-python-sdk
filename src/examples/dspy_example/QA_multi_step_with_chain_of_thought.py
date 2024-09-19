import dspy
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from dotenv import load_dotenv

load_dotenv()

langtrace.init(disable_instrumentations={"all_except": ["dspy", "anthropic"]})

# configure the language model to be used by dspy
llm = dspy.Claude()
dspy.settings.configure(lm=llm)


# create a signature for basic question answering
class BasicQA(dspy.Signature):
    """Given a question, generate the answer."""

    question = dspy.InputField(desc="User's question")
    answer = dspy.OutputField(desc="often between 1 and 5 words")


class DoubleChainOfThought(dspy.Module):
    def __init__(self):
        self.cot1 = dspy.ChainOfThought("question -> step_by_step_thought")
        self.cot2 = dspy.ChainOfThought("question, thought -> one_word_answer")

    def forward(self, question):
        thought = self.cot1(question=question).step_by_step_thought
        answer = self.cot2(question=question, thought=thought).one_word_answer
        return dspy.Prediction(thought=thought, answer=answer)


@with_langtrace_root_span(name="Double Chain Of thought")
def main():
    multi_step_question = "what is the capital of the birth state of the person who provided the assist for the Mario Gotze's in football world cup in 2014?"
    double_cot = DoubleChainOfThought()
    result = double_cot(question=multi_step_question)
    print(result)


main()
