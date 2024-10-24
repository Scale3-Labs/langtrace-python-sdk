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

from typing import Collection
from importlib_metadata import version as v
from wrapt import wrap_function_wrapper as _W
from .patch import generic_patch
from langtrace_python_sdk.constants.instrumentation.pymongo import APIS


class PyMongoInstrumentation(BaseInstrumentor):
    """
    The PyMongoInstrumentation class represents the PyMongo instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["pymongo >= 4.0.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = v("pymongo")
        for api in APIS.values():
            _W(
                module=api["MODULE"],
                name=api["METHOD"],
                wrapper=generic_patch(api["SPAN_NAME"], version, tracer),
            )

    def _uninstrument(self, **kwargs):
        pass
