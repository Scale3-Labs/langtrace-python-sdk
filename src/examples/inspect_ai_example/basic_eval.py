import fsspec
from inspect_ai import Task, task
from inspect_ai.dataset import csv_dataset, Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import chain_of_thought, self_critique
from langtrace_python_sdk.extensions.langtrace_filesystem import LangTraceFileSystem


# Manually register the filesystem with fsspec
# Note: This is only necessary because the filesystem is not registered.
fsspec.register_implementation(LangTraceFileSystem.protocol, LangTraceFileSystem)

question = "What is the price?"


def hydrate_with_question(record):
    # add context to input
    record["input"] = f"Context: {record['input']}\n question: {question}"

    return Sample(
        input=record["input"],
        target=record["target"],
    )


@task
def pricing_question():
    return Task(
        dataset=csv_dataset("langtracefs://clyythmcs0001145cuvi426zi", hydrate_with_question),
        plan=[chain_of_thought(), self_critique()],
        scorer=model_graded_qa(),
    )
