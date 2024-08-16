"""
Copyright (c) 2024 Scale3 Labs

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W
from typing import Collection
from importlib_metadata import version as v
from .patch import patch_bootstrapfewshot_optimizer, patch_signature, patch_evaluate


class DspyInstrumentation(BaseInstrumentor):
    """
    The DspyInstrumentor class represents the DSPy instrumentation"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["dspy-ai >= 2.0.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("dspy-ai")
        _W(
            "dspy.teleprompt.bootstrap",
            "BootstrapFewShot.compile",
            patch_bootstrapfewshot_optimizer(
                "BootstrapFewShot.compile", version, tracer
            ),
        )
        _W(
            "dspy.predict.predict",
            "Predict.forward",
            patch_signature("Predict.forward", version, tracer),
        )
        _W(
            "dspy.predict.chain_of_thought",
            "ChainOfThought.forward",
            patch_signature("ChainOfThought.forward", version, tracer),
        )
        _W(
            "dspy.predict.chain_of_thought_with_hint",
            "ChainOfThoughtWithHint.forward",
            patch_signature("ChainOfThoughtWithHint.forward", version, tracer),
        )
        _W(
            "dspy.predict.react",
            "ReAct.forward",
            patch_signature("ReAct.forward", version, tracer),
        )
        _W(
            "dspy.predict.program_of_thought",
            "ProgramOfThought.forward",
            patch_signature("ProgramOfThought.forward", version, tracer),
        )
        _W(
            "dspy.predict.multi_chain_comparison",
            "MultiChainComparison.forward",
            patch_signature("MultiChainComparison.forward", version, tracer),
        )
        _W(
            "dspy.predict.retry",
            "Retry.forward",
            patch_signature("Retry.forward", version, tracer),
        )
        _W(
            "dspy.evaluate.evaluate",
            "Evaluate.__call__",
            patch_evaluate("Evaluate", version, tracer),
        )

    def _uninstrument(self, **kwargs):
        pass
