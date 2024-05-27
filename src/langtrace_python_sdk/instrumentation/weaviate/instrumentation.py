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
import inspect
import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from langtrace_python_sdk.instrumentation.weaviate.patch import (
    generic_collection_patch, generic_query_patch)

logging.basicConfig(level=logging.FATAL)


class WeaviateInstrumentation(BaseInstrumentor):
    """
    The WeaviateInstrumentation class represents the instrumentation for the Weaviate SDK.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["weaviate-client >= 4.6.1"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version("weaviate-client")

        query_methods = [
            ("weaviate.collections.queries.bm25",
             "_BM25Query.bm25", "weaviate.query.bm25"),
            ("weaviate.collections.queries.fetch_object_by_id",
             "_FetchObjectByIDQuery.fetch_object_by_id", "weaviate.query.fetch_object_by_id"),
            ("weaviate.collections.queries.fetch_objects",
             "_FetchObjectsQuery.fetch_objects", "weaviate.query.fetch_objects"),
            ("weaviate.collections.queries.hybrid",
             "_HybridQuery.hybrid", "weaviate.query.hybrid"),
            ("weaviate.collections.queries.near_object",
             "_NearObjectQuery.near_object", "weaviate.query.near_object"),
            ("weaviate.collections.queries.near_text",
             "_NearTextQuery.near_text", "weaviate.query.near_text"),
            ("weaviate.collections.queries.near_vector",
             "_NearVectorQuery.near_vector", "weaviate.query.near_vector"),
        ]

        for module_path, function_name, api_name in query_methods:
            wrap_function_wrapper(
                module_path,
                function_name,
                generic_query_patch(api_name, version, tracer),
            )

        collection = [
            ("weaviate.collections.collections",
             "_Collections.create", "weaviate.collections.create"),
        ]

        for module_path, function_name, api_name in collection:
            wrap_function_wrapper(
                module_path,
                function_name,
                generic_collection_patch(api_name, version, tracer),
            )

    def _instrument_module(self, module_name):
        pass

    def _uninstrument(self, **kwargs):
        pass
