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
from .patch import patch_crew, patch_memory


class CrewAIInstrumentation(BaseInstrumentor):
    """
    The CrewAIInstrumentation class represents the CrewAI instrumentation"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["crewai >= 0.32.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("crewai")
        try:
            _W(
                "crewai.crew",
                "Crew.kickoff",
                patch_crew("Crew.kickoff", version, tracer),
            )
            _W(
                "crewai.crew",
                "Crew.kickoff_for_each",
                patch_crew("Crew.kickoff_for_each", version, tracer),
            )
            _W(
                "crewai.crew",
                "Crew.kickoff_async",
                patch_crew("Crew.kickoff_async", version, tracer),
            )
            _W(
                "crewai.crew",
                "Crew.kickoff_for_each_async",
                patch_crew("Crew.kickoff_for_each_async", version, tracer),
            )
            _W(
                "crewai.agent",
                "Agent.execute_task",
                patch_crew("Agent.execute_task", version, tracer),
            )
            _W(
                "crewai.task",
                "Task.execute_sync",
                patch_crew("Task.execute", version, tracer),
            )
            _W(
                "crewai.memory.storage.rag_storage",
                "RAGStorage.save",
                patch_memory("RAGStorage.save", version, tracer),
            )
            _W(
                "crewai.memory.storage.rag_storage",
                "RAGStorage.search",
                patch_memory("RAGStorage.search", version, tracer),
            )
            _W(
                "crewai.memory.storage.rag_storage",
                "RAGStorage.reset",
                patch_memory("RAGStorage.reset", version, tracer),
            )
        # pylint: disable=broad-except
        except Exception:
            pass

    def _uninstrument(self, **kwargs):
        pass
