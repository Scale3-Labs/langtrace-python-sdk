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
    """Given a question, generate the answer."""

    question = dspy.InputField(desc="User's question")
    answer = dspy.OutputField(desc="often between 1 and 5 words")


# create a prompt format that says that the llm will take a question and give back an answer
predict = dspy.ChainOfThought(BasicQA)
prediction = predict(
    question="Who provided the assist for the final goal in the 2014 FIFA World Cup final?"
)

print(prediction.answer)
