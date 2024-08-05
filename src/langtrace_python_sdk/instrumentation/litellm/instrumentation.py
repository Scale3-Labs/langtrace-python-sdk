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

from importlib_metadata import version as v
import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper as _W
from .patch import litellm_patch, async_litellm_patch

logging.basicConfig(level=logging.FATAL)


class LiteLLMInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ["litellm >= 1.0.0"]

    def _instrument(self, **kwargs):
        modules_to_instrument = [
            ("litellm.llms.anthropic_text", "AnthropicTextCompletion.completion"),
            ("litellm.llms.anthropic", "AnthropicChatCompletion.completion"),
        ]

        async_modules_to_instrument = [
            ("litellm.llms.anthropic_text", "AnthropicTextCompletion.async_completion"),
            ("litellm.llms.anthropic_text", "AnthropicTextCompletion.async_streaming"),
        ]
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)

        version = v("litellm")

        for module, name in async_modules_to_instrument:
            _W(
                module=module,
                name=name,
                wrapper=async_litellm_patch(name, tracer, version),
            )

        for module, name in modules_to_instrument:
            _W(
                module=module,
                name=name,
                wrapper=litellm_patch(name, tracer, version),
            )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
