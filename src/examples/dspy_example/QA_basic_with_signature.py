import dspy
from langtrace_python_sdk import langtrace
from dotenv import load_dotenv

load_dotenv()

langtrace.init(disable_instrumentations={"all_except": ["dspy", "anthropic"]})

# configure the language model to be used by dspy
llm = dspy.Claude()
dspy.settings.configure(lm=llm)


# create a signature for basic question answering
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""

    question = dspy.InputField(
        desc="A question that can be answered with a short factoid answer"
    )
    answer = dspy.OutputField(desc="often between 1 and 5 words")


# create a prompt format that says that the llm will take a question and give back an answer
predict = dspy.Predict(BasicQA)
prediction = predict(
    question="Sarah has 5 apples. She buys 7 more apples from the store. How many apples does Sarah have now?"
)

print(prediction.answer)
