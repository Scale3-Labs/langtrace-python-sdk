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
import sentry_sdk
import logging
from typing import Dict, Optional, Any
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

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GRPCExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPExporter,
)
from langtrace_python_sdk.constants.exporter.langtrace_exporter import (
    LANGTRACE_REMOTE_URL,
)
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
    LiteLLMInstrumentation,
    LlamaindexInstrumentation,
    MistralInstrumentation,
    AWSBedrockInstrumentation,
    OllamaInstrumentor,
    OpenAIInstrumentation,
    PineconeInstrumentation,
    QdrantInstrumentation,
    AutogenInstrumentation,
    VertexAIInstrumentation,
    WeaviateInstrumentation,
    PyMongoInstrumentation,
    CerebrasInstrumentation,
    MilvusInstrumentation,
)
from opentelemetry.util.re import parse_env_headers

from langtrace_python_sdk.types import DisableInstrumentations, InstrumentationMethods
from langtrace_python_sdk.utils import (
    check_if_sdk_is_outdated,
    get_sdk_version,
    is_package_installed,
    validate_instrumentations,
)
from langtrace_python_sdk.utils.langtrace_sampler import LangtraceSampler
from langtrace_python_sdk.extensions.langtrace_exporter import LangTraceExporter
from sentry_sdk.types import Event, Hint


class LangtraceConfig:
    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key") or os.environ.get("LANGTRACE_API_KEY")
        self.batch = kwargs.get("batch", True)
        self.write_spans_to_console = kwargs.get("write_spans_to_console", False)
        self.custom_remote_exporter = kwargs.get("custom_remote_exporter")
        self.api_host = kwargs.get("api_host", LANGTRACE_REMOTE_URL)
        self.disable_instrumentations = kwargs.get("disable_instrumentations")
        self.disable_tracing_for_functions = kwargs.get("disable_tracing_for_functions")
        self.service_name = kwargs.get("service_name")
        self.disable_logging = kwargs.get("disable_logging", False)
        self.headers = (
            kwargs.get("headers")
            or os.environ.get("LANGTRACE_HEADERS")
            or os.environ.get("OTEL_EXPORTER_OTLP_HEADERS")
        )


def get_host(config: LangtraceConfig) -> str:
    return (
        os.environ.get("LANGTRACE_API_HOST")
        or os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        or config.api_host
        or LANGTRACE_REMOTE_URL
    )


def get_service_name(config: LangtraceConfig):
    service_name = os.environ.get("OTEL_SERVICE_NAME")
    if service_name:
        return service_name

    resource_attributes = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
    if resource_attributes:
        attrs = dict(attr.split("=") for attr in resource_attributes.split(","))
        if "service.name" in attrs:
            return attrs["service.name"]

    if config.service_name:
        return config.service_name

    return sys.argv[0]


def setup_tracer_provider(config: LangtraceConfig, host: str) -> TracerProvider:
    sampler = LangtraceSampler(disabled_methods=config.disable_tracing_for_functions)
    resource = Resource.create(attributes={SERVICE_NAME: get_service_name(config)})
    return TracerProvider(resource=resource, sampler=sampler)


def get_headers(config: LangtraceConfig):
    if not config.headers:
        return {
            "x-api-key": config.api_key,
        }

    if isinstance(config.headers, str):
        return parse_env_headers(config.headers, liberal=True)

    return config.headers


def get_exporter(config: LangtraceConfig, host: str):
    if config.custom_remote_exporter:
        return config.custom_remote_exporter

    headers = get_headers(config)
    host = f"{host}/api/trace" if host == LANGTRACE_REMOTE_URL else host
    if "http" in host.lower() or "https" in host.lower():
        return HTTPExporter(endpoint=host, headers=headers)
    else:
        return GRPCExporter(endpoint=host, headers=headers)


def add_span_processor(provider: TracerProvider, config: LangtraceConfig, exporter):
    if config.write_spans_to_console:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        print(Fore.BLUE + "Writing spans to console" + Fore.RESET)

    elif config.custom_remote_exporter or get_host(config) != LANGTRACE_REMOTE_URL:
        processor = (
            BatchSpanProcessor(exporter)
            if config.batch
            else SimpleSpanProcessor(exporter)
        )
        provider.add_span_processor(processor)
        print(
            Fore.BLUE
            + f"Exporting spans to custom host: {get_host(config)}.."
            + Fore.RESET
        )
    else:
        provider.add_span_processor(BatchSpanProcessor(exporter))
        print(Fore.BLUE + "Exporting spans to Langtrace cloud.." + Fore.RESET)


def init_sentry(config: LangtraceConfig, host: str):
    if os.environ.get("LANGTRACE_ERROR_REPORTING", "True") == "True":
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            before_send=before_send,
        )
        sdk_options = {
            "service_name": os.environ.get("OTEL_SERVICE_NAME")
            or config.service_name
            or sys.argv[0],
            "disable_logging": config.disable_logging,
            "disable_instrumentations": config.disable_instrumentations,
            "disable_tracing_for_functions": config.disable_tracing_for_functions,
            "batch": config.batch,
            "write_spans_to_console": config.write_spans_to_console,
            "custom_remote_exporter": config.custom_remote_exporter,
            "sdk_name": LANGTRACE_SDK_NAME,
            "sdk_version": get_sdk_version(),
            "api_host": host,
        }
        sentry_sdk.set_context("sdk_init_options", sdk_options)


def init(
    api_key: Optional[str] = None,
    batch: bool = True,
    write_spans_to_console: bool = False,
    custom_remote_exporter: Optional[Any] = None,
    api_host: Optional[str] = LANGTRACE_REMOTE_URL,
    disable_instrumentations: Optional[DisableInstrumentations] = None,
    disable_tracing_for_functions: Optional[InstrumentationMethods] = None,
    service_name: Optional[str] = None,
    disable_logging: bool = False,
    headers: Dict[str, str] = {},
):

    check_if_sdk_is_outdated()
    config = LangtraceConfig(
        api_key=api_key,
        batch=batch,
        write_spans_to_console=write_spans_to_console,
        custom_remote_exporter=custom_remote_exporter,
        api_host=api_host,
        disable_instrumentations=disable_instrumentations,
        disable_tracing_for_functions=disable_tracing_for_functions,
        service_name=service_name,
        disable_logging=disable_logging,
        headers=headers,
    )

    if config.disable_logging:
        logging.disable(level=logging.INFO)
        sys.stdout = open(os.devnull, "w")

    host = get_host(config)
    print(Fore.GREEN + "Initializing Langtrace SDK.." + Fore.RESET)
    print(
        Fore.WHITE
        + "⭐ Leave our github a star to stay on top of our updates - https://github.com/Scale3-Labs/langtrace"
        + Fore.RESET
    )

    if host == LANGTRACE_REMOTE_URL and not config.api_key:
        print(Fore.RED)
        print(
            "Missing Langtrace API key, proceed to https://langtrace.ai to create one"
        )
        print("Set the API key as an environment variable LANGTRACE_API_KEY")
        print(Fore.RESET)
        return

    provider = setup_tracer_provider(config, host)
    exporter = get_exporter(config, host)

    os.environ["LANGTRACE_API_HOST"] = host.replace("/api/trace", "")
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
        "litellm": LiteLLMInstrumentation(),
        "anthropic": AnthropicInstrumentation(),
        "cohere": CohereInstrumentation(),
        "weaviate-client": WeaviateInstrumentation(),
        "sqlalchemy": SQLAlchemyInstrumentor(),
        "ollama": OllamaInstrumentor(),
        "dspy-ai": DspyInstrumentation(),
        "crewai": CrewAIInstrumentation(),
        "vertexai": VertexAIInstrumentation(),
        "google-cloud-aiplatform": VertexAIInstrumentation(),
        "google-generativeai": GeminiInstrumentation(),
        "mistralai": MistralInstrumentation(),
        "boto3": AWSBedrockInstrumentation(),
        "autogen": AutogenInstrumentation(),
        "pymongo": PyMongoInstrumentation(),
        "cerebras-cloud-sdk": CerebrasInstrumentation(),
        "pymilvus": MilvusInstrumentation(),
    }

    init_instrumentations(config.disable_instrumentations, all_instrumentations)
    add_span_processor(provider, config, exporter)

    sys.stdout = sys.__stdout__
    init_sentry(config, host)


def before_send(event: Event, hint: Hint):
    # Check if there's an exception and stacktrace in the event
    if "exception" in event:
        exception = event["exception"]["values"][0]
        stacktrace = exception.get("stacktrace", {})
        frames = stacktrace.get("frames", [])
        if frames:
            last_frame = frames[-1]
            absolute_path = last_frame.get("abs_path")  # Absolute path
            # Check if the error is from the SDK
            if "langtrace-python-sdk" in absolute_path:
                return event

    return None


def init_instrumentations(
    disable_instrumentations: Optional[DisableInstrumentations],
    all_instrumentations: dict,
):
    if disable_instrumentations is None:
        for name, v in all_instrumentations.items():
            if is_package_installed(name):
                try:
                    v.instrument()
                except Exception as e:
                    print(f"Skipping {name} due to error while instrumenting: {e}")

    else:

        validate_instrumentations(disable_instrumentations)

        for key in disable_instrumentations:
            vendors = [k.value for k in disable_instrumentations[key]]

        key = next(iter(disable_instrumentations))
        filtered_dict = {}
        if key == "all_except":
            filtered_dict = {
                k: v for k, v in all_instrumentations.items() if k in vendors
            }
        elif key == "only":
            filtered_dict = {
                k: v for k, v in all_instrumentations.items() if k not in vendors
            }

        for name, v in filtered_dict.items():
            if is_package_installed(name):
                try:
                    v.instrument()
                except Exception as e:
                    print(f"Skipping {name} due to error while instrumenting: {e}")
