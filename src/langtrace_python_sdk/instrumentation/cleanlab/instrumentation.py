"""
Copyright (c) 2025 Scale3 Labs
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

import importlib.metadata
import logging
from typing import Any, Collection, Optional

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import TracerProvider, get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.cleanlab.patch import generic_patch

logging.basicConfig(level=logging.FATAL)


class CleanLabInstrumentation(BaseInstrumentor):  # type: ignore

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["cleanlab-tlm >= 1.0.7", "trace-attributes >= 4.0.5"]

    def _instrument(self, **kwargs: Any) -> None:
        tracer_provider: Optional[TracerProvider] = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version: str = importlib.metadata.version("cleanlab_tlm")

        wrap_function_wrapper(
            "cleanlab_tlm.tlm",
            "TLM.prompt",
            generic_patch(version, tracer),
        )

        wrap_function_wrapper(
            "cleanlab_tlm.tlm",
            "TLM.get_trustworthiness_score",
            generic_patch(version, tracer),
        )

        wrap_function_wrapper(
            "cleanlab_tlm.tlm",
            "TLM.try_prompt",
            generic_patch(version, tracer),
        )

        wrap_function_wrapper(
            "cleanlab_tlm.tlm",
            "TLM.try_get_trustworthiness_score",
            generic_patch(version, tracer),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        pass
