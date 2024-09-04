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

from langtrace_python_sdk.constants.instrumentation.weaviate import APIS
from langtrace_python_sdk.instrumentation.weaviate.patch import (
    generic_collection_patch,
    generic_query_patch,
)

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logging


class WeaviateInstrumentation(BaseInstrumentor):
    """
    The WeaviateInstrumentation class represents the instrumentation for the Weaviate SDK.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["weaviate-client >= 4.6.1", "trace-attributes >= 7.0.3"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("weaviate-client")

        for api_name, api_config in APIS.items():
            if api_config.get("OPERATION") in ["query", "generate"]:
                wrap_function_wrapper(
                    api_config["MODULE"],
                    api_config["METHOD"],
                    generic_query_patch(api_name, version, tracer),
                )
            elif api_config.get("OPERATION") == "create":
                wrap_function_wrapper(
                    api_config["MODULE"],
                    api_config["METHOD"],
                    generic_collection_patch(api_name, version, tracer),
                )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
