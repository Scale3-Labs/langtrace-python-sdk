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

from typing import Collection

from importlib_metadata import version as v
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W

from .patch import patch_run


class CrewaiToolsInstrumentation(BaseInstrumentor):
    """
    The CrewAIInstrumentation class represents the CrewAI instrumentation"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["crewai-tools >= 0.32.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("crewai-tools")
        try:
            _W(
                "crewai_tools.tools.serper_dev_tool.serper_dev_tool",
                "SerperDevTool._run",
                patch_run("SerperDevTool._run", version, tracer),
            )
        # pylint: disable=broad-except
        except Exception:
            pass

    def _uninstrument(self, **kwargs):
        pass
