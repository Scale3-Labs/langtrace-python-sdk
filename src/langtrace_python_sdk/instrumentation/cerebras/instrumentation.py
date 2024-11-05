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

from typing import Collection
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from opentelemetry.semconv.schemas import Schemas
from wrapt import wrap_function_wrapper
from importlib_metadata import version as v
from .patch import chat_completions_create, async_chat_completions_create


class CerebrasInstrumentation(BaseInstrumentor):
    """
    The CerebrasInstrumentation class represents the Cerebras instrumentation
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["cerebras-cloud-sdk >= 1.0.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__, "", tracer_provider, schema_url=Schemas.V1_27_0.value
        )
        version = v("cerebras-cloud-sdk")

        wrap_function_wrapper(
            module="cerebras.cloud.sdk",
            name="resources.chat.completions.CompletionsResource.create",
            wrapper=chat_completions_create(version, tracer),
        )

        wrap_function_wrapper(
            module="cerebras.cloud.sdk",
            name="resources.chat.completions.AsyncCompletionsResource.create",
            wrapper=async_chat_completions_create(version, tracer),
        )

    def _uninstrument(self, **kwargs):
        pass
