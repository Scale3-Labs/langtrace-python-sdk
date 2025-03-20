"""
Copyright (c) 2025 Scale3 Labs

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
from opentelemetry import trace
from wrapt import wrap_function_wrapper as _W
from importlib.metadata import version as v
from .patch import patch_graphrag_search, patch_kg_pipeline_run, \
patch_kg_pipeline_run, patch_retriever_search


class Neo4jGraphRAGInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["neo4j-graphrag>=1.6.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = trace.get_tracer(__name__, "", tracer_provider)
        graphrag_version = v("neo4j-graphrag")
        
        try:
            # instrument kg builder
            _W(
                "neo4j_graphrag.experimental.pipeline.kg_builder",
                "SimpleKGPipeline.run_async",
                patch_kg_pipeline_run("run_async", graphrag_version, tracer),
            )
            
            # Instrument GraphRAG
            _W(
                "neo4j_graphrag.generation.graphrag",
                "GraphRAG.search",
                patch_graphrag_search("search", graphrag_version, tracer),
            )
            
            # Instrument retrievers
            _W(
                "neo4j_graphrag.retrievers.vector",
                "VectorRetriever.get_search_results",
                patch_retriever_search("vector_search", graphrag_version, tracer),
            )
            
        except Exception as e:
            print(f"Failed to instrument Neo4j GraphRAG: {e}")

    def _uninstrument(self, **kwargs):
        pass