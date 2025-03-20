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
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.constants.instrumentation.neo4j import APIS
from langtrace_python_sdk.instrumentation.neo4j.patch import (
    session_patch, 
    driver_patch,
    transaction_patch
)

logging.basicConfig(level=logging.FATAL)


class Neo4jInstrumentation(BaseInstrumentor):
    """
    The Neo4jInstrumentation class represents the Neo4j graph database instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["neo4j >= 5.25.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("neo4j")
        
        wrap_function_wrapper(
            "neo4j._sync.driver",
            "Driver.execute_query",
            driver_patch("EXECUTE_QUERY", version, tracer),
        )

    def _uninstrument(self, **kwargs):
        pass