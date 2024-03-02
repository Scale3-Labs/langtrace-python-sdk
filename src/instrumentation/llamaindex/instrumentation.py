from typing import Collection

import llama_index
from langtrace.trace_attributes import LlamaIndexMethods
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from instrumentation.llamaindex.patch import generic_patch

MODULES = [
    "llama_index.core.query_pipeline.query",
]


class LlamaindexInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["llama-index >= 0.10.0"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)

        wrap_function_wrapper(
            'llama_index.core.base.base_query_engine',
            'BaseQueryEngine.query',
            generic_patch(LlamaIndexMethods.QUERYENGINE_QUERY.value,
                          'query', tracer, llama_index.core.__version__)
        )
        wrap_function_wrapper(
            'llama_index.core.base.base_retriever',
            'BaseRetriever.retrieve',
            generic_patch(LlamaIndexMethods.RETRIEVER_RETRIEVE.value,
                          'retrieve', tracer, llama_index.core.__version__)
        )
        wrap_function_wrapper(
            'llama_index.core.extractors.interface',
            'BaseExtractor.extract',
            generic_patch(
                LlamaIndexMethods.BASEEXTRACTOR_EXTRACT.value, 'extract', tracer, llama_index.core.__version__)
        )
        wrap_function_wrapper(
            'llama_index.core.extractors.interface',
            'BaseExtractor.aextract',
            generic_patch(
                LlamaIndexMethods.BASEEXTRACTOR_AEXTRACT.value, 'extract', tracer, llama_index.core.__version__)
        )
        wrap_function_wrapper(
            'llama_index.core.readers.file.base',
            'SimpleDirectoryReader.load_data',
            generic_patch(
                LlamaIndexMethods.BASEREADER_LOADDATA.value, 'loaddata', tracer, llama_index.core.__version__)
        )
        wrap_function_wrapper(
            'llama_index.core.chat_engine.types',
            'BaseChatEngine.chat',
            generic_patch(
                LlamaIndexMethods.CHATENGINE_CHAT.value, 'chat', tracer, llama_index.core.__version__)
        )
        wrap_function_wrapper(
            'llama_index.core.chat_engine.types',
            'BaseChatEngine.achat',
            generic_patch(
                LlamaIndexMethods.CHATENGINE_ACHAT.value, 'chat', tracer, llama_index.core.__version__)
        )

    def _instrument_module(self, module_name):
        print(module_name)

    def _uninstrument(self, **kwargs):
        print(kwargs)
