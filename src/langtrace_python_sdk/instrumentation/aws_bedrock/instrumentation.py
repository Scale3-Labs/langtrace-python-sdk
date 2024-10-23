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
from wrapt import wrap_function_wrapper as _W

from langtrace_python_sdk.instrumentation.aws_bedrock.patch import (
    converse, converse_stream
)

logging.basicConfig(level=logging.FATAL)

def _patch_client(client, version: str, tracer) -> None:

    # Store original methods
    original_converse = client.converse

    # Replace with wrapped versions
    client.converse = converse("aws_bedrock.converse", version, tracer)(original_converse)

class AWSBedrockInstrumentation(BaseInstrumentor):
    
    def instrumentation_dependencies(self) -> Collection[str]:
        return ["boto3 >= 1.35.31"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("boto3")

        def wrap_create_client(wrapped, instance, args, kwargs):
            result = wrapped(*args, **kwargs)
            if args and args[0] == 'bedrock-runtime':
                _patch_client(result, version, tracer)
            return result

        _W("boto3", "client", wrap_create_client)

    def _uninstrument(self, **kwargs):
        pass