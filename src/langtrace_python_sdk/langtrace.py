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

import os
import sys
from typing import Optional
import importlib.util
from colorama import Fore
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME, SENTRY_DSN
from opentelemetry import trace
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from langtrace_python_sdk.constants.exporter.langtrace_exporter import (
    LANGTRACE_REMOTE_URL,
)
from langtrace_python_sdk.extensions.langtrace_exporter import LangTraceExporter
from langtrace_python_sdk.instrumentation import (
    AnthropicInstrumentation,
    ChromaInstrumentation,
    CohereInstrumentation,
    CrewAIInstrumentation,
    DspyInstrumentation,
    EmbedchainInstrumentation,
    GeminiInstrumentation,
    GroqInstrumentation,
    LangchainCommunityInstrumentation,
    LangchainCoreInstrumentation,
    LangchainInstrumentation,
    LanggraphInstrumentation,
    LlamaindexInstrumentation,
    MistralInstrumentation,
    OllamaInstrumentor,
    OpenAIInstrumentation,
    PineconeInstrumentation,
    QdrantInstrumentation,
    AutogenInstrumentation,
    VertexAIInstrumentation,
    WeaviateInstrumentation,
)
from langtrace_python_sdk.types import (
    DisableInstrumentations,
    InstrumentationMethods,
    InstrumentationType,
)
from langtrace_python_sdk.utils import check_if_sdk_is_outdated, get_sdk_version
from langtrace_python_sdk.utils.langtrace_sampler import LangtraceSampler
import sentry_sdk


def init(
    api_key: str = None,
    batch: bool = True,
    write_spans_to_console: bool = False,
    custom_remote_exporter=None,
    api_host: Optional[str] = LANGTRACE_REMOTE_URL,
    disable_instrumentations: Optional[DisableInstrumentations] = None,
    disable_tracing_for_functions: Optional[InstrumentationMethods] = None,
    service_name: Optional[str] = None,
    disable_logging=False,
):
    if disable_logging:
        sys.stdout = open(os.devnull, "w")

    host = (
        os.environ.get("LANGTRACE_API_HOST", None)
        or os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", None)
        or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", None)
        or api_host
        or LANGTRACE_REMOTE_URL
    )
    check_if_sdk_is_outdated()
    print(Fore.GREEN + "Initializing Langtrace SDK.." + Fore.RESET)
    print(
        Fore.WHITE
        + "⭐ Leave our github a star to stay on top of our updates - https://github.com/Scale3-Labs/langtrace"
        + Fore.RESET
    )
    sampler = LangtraceSampler(disabled_methods=disable_tracing_for_functions)
    resource = Resource.create(
        attributes={
            SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME")
            or service_name
            or sys.argv[0]
        }
    )
    provider = TracerProvider(resource=resource, sampler=sampler)

    remote_write_exporter = (
        LangTraceExporter(
            api_key=api_key, api_host=host, disable_logging=disable_logging
        )
        if custom_remote_exporter is None
        else custom_remote_exporter
    )
    console_exporter = ConsoleSpanExporter()
    batch_processor_remote = BatchSpanProcessor(remote_write_exporter)
    simple_processor_remote = SimpleSpanProcessor(remote_write_exporter)
    simple_processor_console = SimpleSpanProcessor(console_exporter)

    os.environ["LANGTRACE_API_HOST"] = host.replace("/api/trace", "")
    # Initialize tracer
    trace.set_tracer_provider(provider)
    all_instrumentations = {
        "openai": OpenAIInstrumentation(),
        "groq": GroqInstrumentation(),
        "pinecone-client": PineconeInstrumentation(),
        "llama-index": LlamaindexInstrumentation(),
        "chromadb": ChromaInstrumentation(),
        "embedchain": EmbedchainInstrumentation(),
        "qdrant-client": QdrantInstrumentation(),
        "langchain": LangchainInstrumentation(),
        "langchain-core": LangchainCoreInstrumentation(),
        "langchain-community": LangchainCommunityInstrumentation(),
        "langgraph": LanggraphInstrumentation(),
        "anthropic": AnthropicInstrumentation(),
        "cohere": CohereInstrumentation(),
        "weaviate-client": WeaviateInstrumentation(),
        "sqlalchemy": SQLAlchemyInstrumentor(),
        "ollama": OllamaInstrumentor(),
        "dspy-ai": DspyInstrumentation(),
        "crewai": CrewAIInstrumentation(),
        "google-cloud-aiplatform": VertexAIInstrumentation(),
        "google-generativeai": GeminiInstrumentation(),
        "mistralai": MistralInstrumentation(),
        "autogen": AutogenInstrumentation(),
    }

    init_instrumentations(disable_instrumentations, all_instrumentations)
    if write_spans_to_console:
        print(Fore.BLUE + "Writing spans to console" + Fore.RESET)
        provider.add_span_processor(simple_processor_console)

    elif custom_remote_exporter is not None:
        print(Fore.BLUE + "Exporting spans to custom remote exporter.." + Fore.RESET)
        if batch:
            provider.add_span_processor(batch_processor_remote)
        else:
            provider.add_span_processor(simple_processor_remote)

    elif host != LANGTRACE_REMOTE_URL:
        print(Fore.BLUE + f"Exporting spans to custom host: {host}.." + Fore.RESET)
        if batch:
            provider.add_span_processor(batch_processor_remote)
        else:
            provider.add_span_processor(simple_processor_remote)
    else:
        print(Fore.BLUE + "Exporting spans to Langtrace cloud.." + Fore.RESET)
        provider.add_span_processor(batch_processor_remote)

    sys.stdout = sys.__stdout__
    if os.environ.get("LANGTRACE_ERROR_REPORTING", "True") == "True":
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
        sdk_options = {
            "service_name": os.environ.get("OTEL_SERVICE_NAME")
            or service_name
            or sys.argv[0],
            "disable_logging": disable_logging,
            "disable_instrumentations": disable_instrumentations,
            "disable_tracing_for_functions": disable_tracing_for_functions,
            "batch": batch,
            "write_spans_to_console": write_spans_to_console,
            "custom_remote_exporter": custom_remote_exporter,
            "sdk_name": LANGTRACE_SDK_NAME,
            "sdk_version": get_sdk_version(),
            "api_host": host,
        }
        sentry_sdk.set_context("sdk_init_options", sdk_options)


def init_instrumentations(
    disable_instrumentations: DisableInstrumentations, all_instrumentations: dict
):
    if disable_instrumentations is None:
        for idx, (name, v) in enumerate(all_instrumentations.items()):
            if is_package_installed(name):
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


def is_package_installed(package_name):
    import pkg_resources

    installed_packages = {p.key for p in pkg_resources.working_set}
    return package_name in installed_packages
