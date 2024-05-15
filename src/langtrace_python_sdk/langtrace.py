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

from typing import Optional

from langtrace_python_sdk.types import DisableInstrumentations, InstrumentationType
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from langtrace_python_sdk.extensions.langtrace_exporter import LangTraceExporter
from langtrace_python_sdk.instrumentation.anthropic.instrumentation import (
    AnthropicInstrumentation,
)
from langtrace_python_sdk.instrumentation.chroma.instrumentation import (
    ChromaInstrumentation,
)
from langtrace_python_sdk.instrumentation.cohere.instrumentation import (
    CohereInstrumentation,
)
from langtrace_python_sdk.instrumentation.groq.instrumentation import (
    GroqInstrumentation,
)
from langtrace_python_sdk.instrumentation.langchain.instrumentation import (
    LangchainInstrumentation,
)
from langtrace_python_sdk.instrumentation.langchain_community.instrumentation import (
    LangchainCommunityInstrumentation,
)
from langtrace_python_sdk.instrumentation.langchain_core.instrumentation import (
    LangchainCoreInstrumentation,
)
from langtrace_python_sdk.instrumentation.langgraph.instrumentation import (
    LanggraphInstrumentation,
)
from langtrace_python_sdk.instrumentation.llamaindex.instrumentation import (
    LlamaindexInstrumentation,
)
from langtrace_python_sdk.instrumentation.openai.instrumentation import (
    OpenAIInstrumentation,
)
from langtrace_python_sdk.instrumentation.pinecone.instrumentation import (
    PineconeInstrumentation,
)
from langtrace_python_sdk.instrumentation.qdrant.instrumentation import (
    QdrantInstrumentation,
)


def init(
    api_key: str = None,
    batch: bool = True,
    write_spans_to_console: bool = False,
    custom_remote_exporter=None,
    api_host: Optional[str] = None,
    disable_instrumentations: Optional[DisableInstrumentations] = None,
):
    provider = TracerProvider()

    remote_write_exporter = (
        LangTraceExporter(api_key=api_key, api_host=api_host)
        if custom_remote_exporter is None
        else custom_remote_exporter
    )
    console_exporter = ConsoleSpanExporter()
    batch_processor_remote = BatchSpanProcessor(remote_write_exporter)
    simple_processor_remote = SimpleSpanProcessor(remote_write_exporter)
    simple_processor_console = SimpleSpanProcessor(console_exporter)

    if write_spans_to_console:
        provider.add_span_processor(simple_processor_console)

    elif custom_remote_exporter is not None:
        if batch:
            provider.add_span_processor(batch_processor_remote)
        else:
            provider.add_span_processor(simple_processor_remote)

    elif api_host is not None:
        if batch:
            provider.add_span_processor(batch_processor_remote)
        else:
            provider.add_span_processor(simple_processor_remote)
    else:
        provider.add_span_processor(batch_processor_remote)

    # Initialize tracer
    trace.set_tracer_provider(provider)

    all_instrumentations = {
        "openai": OpenAIInstrumentation(),
        "groq": GroqInstrumentation(),
        "pinecone": PineconeInstrumentation(),
        "llamaindex": LlamaindexInstrumentation(),
        "chroma": ChromaInstrumentation(),
        "qdrant": QdrantInstrumentation(),
        "langchain": LangchainInstrumentation(),
        "langchain_core": LangchainCoreInstrumentation(),
        "langchain_community": LangchainCommunityInstrumentation(),
        "langgraph": LanggraphInstrumentation(),
        "anthropic": AnthropicInstrumentation(),
        "cohere": CohereInstrumentation(),
    }

    init_instrumentations(disable_instrumentations, all_instrumentations)


def init_instrumentations(
    disable_instrumentations: DisableInstrumentations, all_instrumentations: dict
):
    if disable_instrumentations is None:
        for _, v in all_instrumentations.items():
            v.instrument()
    else:

        validate_instrumentations(disable_instrumentations)

        for key in disable_instrumentations:
            for vendor in disable_instrumentations[key]:
                if key == "only":
                    filtered_dict = {
                        k: v
                        for k, v in all_instrumentations.items()
                        if k != vendor.value
                    }
                    for _, v in filtered_dict.items():
                        v.instrument()
                else:
                    filtered_dict = {
                        k: v
                        for k, v in all_instrumentations.items()
                        if k == vendor.value
                    }

                    for _, v in filtered_dict.items():
                        v.instrument()


def validate_instrumentations(disable_instrumentations):
    if disable_instrumentations is not None:
        for key, value in disable_instrumentations.items():
            if isinstance(value, str):
                # Convert single string to list of enum values
                disable_instrumentations[key] = [InstrumentationType.from_string(value)]
            elif isinstance(value, list):
                # Convert list of strings to list of enum values
                disable_instrumentations[key] = [
                    (
                        InstrumentationType.from_string(item)
                        if isinstance(item, str)
                        else item
                    )
                    for item in value
                ]
            # Validate all items are of enum type
            if not all(
                isinstance(item, InstrumentationType)
                for item in disable_instrumentations[key]
            ):
                raise TypeError(
                    f"All items in {key} must be of type InstrumentationType"
                )
        if (
            disable_instrumentations.get("all_except") is not None
            and disable_instrumentations.get("only") is not None
        ):
            raise ValueError(
                "Cannot specify both only and all_except in disable_instrumentations"
            )
