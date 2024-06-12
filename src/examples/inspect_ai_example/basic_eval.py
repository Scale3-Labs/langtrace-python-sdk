# langtrace.init(write_spans_to_console=True)
import fsspec
from inspect_ai import Task, task
from inspect_ai.dataset import example_dataset
from inspect_ai.scorer import model_graded_fact
from inspect_ai.solver import chain_of_thought, generate, self_critique

from langtrace_python_sdk.extensions.langtrace_filesystem import \
    LangTraceFileSystem

# from langtrace_python_sdk import langtrace


# Manually register the filesystem with fsspec
# Note: This is only necessary because the filesystem is not registered.
fsspec.register_implementation(LangTraceFileSystem.protocol, LangTraceFileSystem)


@task
def security_guide():
    return Task(
        dataset=example_dataset("security_guide"),
        plan=[
            chain_of_thought(),
            generate(),
            self_critique()
        ],
        scorer=model_graded_fact()
    )
