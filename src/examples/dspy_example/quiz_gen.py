import dspy
from dspy.predict import Retry
from dspy.datasets import HotPotQA
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from dspy.evaluate.evaluate import Evaluate
from dspy.primitives.assertions import assert_transform_module, backtrack_handler
import sys
import os
import dspy

# Add the local src folder to the Python path
sys.path.insert(0, os.path.abspath('/Users/karthikkalyanaraman/work/langtrace/langtrace-python-sdk/src'))

# flake8: noqa
from langtrace_python_sdk import langtrace, with_langtrace_root_span
langtrace.init()


colbertv2_wiki17_abstracts = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.settings.configure(rm=colbertv2_wiki17_abstracts)
turbo = dspy.OpenAI(model='gpt-3.5-turbo-0613', max_tokens=500)
dspy.settings.configure(lm=turbo, trace=[], temperature=0.7)

dataset = HotPotQA(train_seed=1, train_size=300, eval_seed=2023, dev_size=300, test_size=0, keep_details=True)
trainset = [x.with_inputs('question', 'answer') for x in dataset.train]
devset = [x.with_inputs('question', 'answer') for x in dataset.dev]

class GenerateAnswerChoices(dspy.Signature):
    """Generate answer choices in JSON format that include the correct answer and plausible distractors for the specified question."""
    question = dspy.InputField()
    correct_answer = dspy.InputField()
    number_of_choices = dspy.InputField()
    answer_choices = dspy.OutputField(desc='JSON key-value pairs')

class QuizAnswerGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_choices = dspy.ChainOfThought(GenerateAnswerChoices)

    def forward(self, question, answer):
        choices = self.generate_choices(question=question, correct_answer=answer, number_of_choices='4').answer_choices
        return dspy.Prediction(choices = choices)

@with_langtrace_root_span(name="quiz_gen_example")
def example():
    quiz_generator = QuizAnswerGenerator()

    question = 'What is the capital of France?'
    result = quiz_generator(question=question, answer='Paris')
    print(result)

if __name__ == '__main__':
    example()
