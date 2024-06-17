import dspy
import json
from dspy.datasets import HotPotQA
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.evaluate import Evaluate

# flake8: noqa
from langtrace_python_sdk import langtrace, with_langtrace_root_span

langtrace.init()


colbertv2_wiki17_abstracts = dspy.ColBERTv2(
    url="http://20.102.90.50:2017/wiki17_abstracts"
)
dspy.settings.configure(rm=colbertv2_wiki17_abstracts)
turbo = dspy.OpenAI(model="gpt-3.5-turbo-0613", max_tokens=500)
dspy.settings.configure(lm=turbo, trace=[], temperature=0.7)

dataset = HotPotQA(
    train_seed=1,
    train_size=300,
    eval_seed=2023,
    dev_size=300,
    test_size=0,
    keep_details=True,
)
trainset = [x.with_inputs("question", "answer") for x in dataset.train]
devset = [x.with_inputs("question", "answer") for x in dataset.dev]


class GenerateAnswerChoices(dspy.Signature):
    """Generate answer choices in JSON format that include the correct answer and plausible distractors for the specified question."""

    question = dspy.InputField()
    correct_answer = dspy.InputField()
    number_of_choices = dspy.InputField()
    answer_choices = dspy.OutputField(desc="JSON key-value pairs")


class QuizAnswerGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(GenerateAnswerChoices)

    def forward(self, question, answer):
        choices = self.prog(
            question=question, correct_answer=answer, number_of_choices="4"
        ).answer_choices
        # dspy.Suggest(
        #     format_checker(choices),
        #     "The format of the answer choices should be in JSON format. Please revise accordingly.",
        #     target_module=GenerateAnswerChoices,
        # )
        return dspy.Prediction(choices=choices)


def format_checker(choice_string):
    try:
        choices = json.loads(choice_string)
        if isinstance(choices, dict) and all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in choices.items()
        ):
            return True
    except json.JSONDecodeError:
        return False

    return False


def format_valid_metric(gold, pred, trace=None):
    generated_choices = pred.choices
    format_valid = format_checker(generated_choices)
    score = format_valid
    return score


@with_langtrace_root_span(name="quiz_generator_1")
def quiz_generator_1():
    quiz_generator = QuizAnswerGenerator()

    example = devset[67]
    print("Example Question: ", example.question)
    print("Example Answer: ", example.answer)
    # quiz_choices = quiz_generator(question=example.question, answer=example.answer)
    # print("Generated Quiz Choices: ", quiz_choices.choices)

    optimizer = BootstrapFewShot(
        metric=format_valid_metric, max_bootstrapped_demos=4, max_labeled_demos=4
    )
    compiled_quiz_generator = optimizer.compile(
        quiz_generator,
        trainset=trainset,
    )
    quiz_choices = compiled_quiz_generator(
        question=example.question, answer=example.answer
    )
    print("Generated Quiz Choices: ", quiz_choices.choices)

    # Evaluate
    evaluate = Evaluate(
        metric=format_valid_metric,
        devset=devset[67:70],
        num_threads=1,
        display_progress=True,
        display_table=5,
    )
    evaluate(quiz_generator)


if __name__ == "__main__":
    quiz_generator_1()
