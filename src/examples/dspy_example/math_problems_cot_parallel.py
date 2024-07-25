import contextvars
import dspy
from dspy.datasets.gsm8k import GSM8K, gsm8k_metric
from dspy.teleprompt import BootstrapFewShot
from concurrent.futures import ThreadPoolExecutor

# flake8: noqa
from langtrace_python_sdk import langtrace, with_langtrace_root_span, inject_additional_attributes

langtrace.init()

turbo = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=250)
dspy.settings.configure(lm=turbo)

# Load math questions from the GSM8K dataset
gsm8k = GSM8K()
gsm8k_trainset, gsm8k_devset = gsm8k.train[:10], gsm8k.dev[:10]

class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        result = inject_additional_attributes(lambda: self.prog(question=question), {'langtrace.span.name': 'MathProblemsCotParallel'})
        return result

@with_langtrace_root_span(name="parallel_example")
def example():
    # Set up the optimizer: we want to "bootstrap" (i.e., self-generate) 4-shot examples of our CoT program.
    config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

    # Optimize! Use the `gsm8k_metric` here. In general, the metric is going to tell the optimizer how well it's doing.
    teleprompter = BootstrapFewShot(metric=gsm8k_metric, **config)
    optimized_cot = teleprompter.compile(CoT(), trainset=gsm8k_trainset)

    questions = [
        "What is the sine of 0?",
        "What is the tangent of 100?",
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(contextvars.copy_context().run, optimized_cot, question=q) for q in questions]

        for future in futures:
            ans = future.result()
            print(ans)


if __name__ == "__main__":
    example()
