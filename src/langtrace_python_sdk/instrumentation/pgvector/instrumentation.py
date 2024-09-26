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

import importlib.metadata
import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.constants.instrumentation.pgvector import APIS
from langtrace_python_sdk.instrumentation.pgvector.patch import (
    generic_patch,
)

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logging


class PgVectorInstrumentation(BaseInstrumentor):
    """
    The PgVectorInstrumentation class represents the instrumentation for the Postgres Vector.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["pgvector >= 0.3.3", "trace-attributes >= 7.1.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("pgvector")

        print("Instrumenting PgVector")
        for api_name, api_config in APIS.items():
            wrap_function_wrapper(
                api_config["MODULE"],
                api_config["METHOD"],
                generic_patch(api_name, version, tracer),
            )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
