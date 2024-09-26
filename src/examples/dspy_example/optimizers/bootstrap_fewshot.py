import dspy
from dotenv import find_dotenv, load_dotenv
from dspy.datasets import HotPotQA
from dspy.teleprompt import BootstrapFewShot

from langtrace_python_sdk import inject_additional_attributes, langtrace

_ = load_dotenv(find_dotenv())

langtrace.init()

turbo = dspy.LM('openai/gpt-4o-mini')
colbertv2_wiki17_abstracts = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')

dspy.settings.configure(lm=turbo, rm=colbertv2_wiki17_abstracts)


# Load the dataset.
dataset = HotPotQA(train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0)

# Tell DSPy that the 'question' field is the input. Any other fields are labels and/or metadata.
trainset = [x.with_inputs('question') for x in dataset.train]
devset = [x.with_inputs('question') for x in dataset.dev]


class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)


# Validation logic: check that the predicted answer is correct.
# Also check that the retrieved context does actually contain that answer.
def validate_context_and_answer(example, prediction, trace=None):
    answer_em = dspy.evaluate.answer_exact_match(example, prediction)
    answer_pm = dspy.evaluate.answer_passage_match(example, prediction)
    return answer_em and answer_pm


# Set up a basic optimizer, which will compile our RAG program.
optimizer = BootstrapFewShot(metric=validate_context_and_answer)

# Compile!
compiled_rag = optimizer.compile(RAG(), trainset=trainset)

# Ask any question you like to this simple RAG program.
my_question = "Who was the hero of the movie peraanmai?"

# Get the prediction. This contains `pred.context` and `pred.answer`.
# pred = compiled_rag(my_question)
pred = inject_additional_attributes(lambda: compiled_rag(my_question), {'experiment': 'experiment 6', 'description': 'trying additional stuff', 'run_id': 'run_1'})
# compiled_rag.save('compiled_rag_v1.json')

# Print the contexts and the answer.
print(f"Question: {my_question}")
print(f"Predicted Answer: {pred.answer}")
print(f"Retrieved Contexts (truncated): {[c[:200] + '...' for c in pred.context]}")

# print("Inspecting the history of the optimizer:")
# turbo.inspect_history(n=1)

from dspy.evaluate import Evaluate


def validate_answer(example, pred, trace=None):
    return True


# Set up the evaluator, which can be used multiple times.
evaluate = Evaluate(devset=devset, metric=validate_answer, num_threads=4, display_progress=True, display_table=0)


# Evaluate our `optimized_cot` program.
evaluate(compiled_rag)
