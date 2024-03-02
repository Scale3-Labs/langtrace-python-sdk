import importlib.metadata
from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from instrumentation.langchain.patch import generic_patch, runnable_patch


class LangchainInstrumentation(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["langchain-core >= 0.1.27"]

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, "", tracer_provider)
        version = importlib.metadata.version('chromadb')

        # Retriever
        wrap_function_wrapper(
            'langchain_core.retrievers',
            'BaseRetriever.get_relevant_documents',
            generic_patch(
                'BaseRetriever.get_relevant_documents', 'retriever', tracer, version)
        )

        wrap_function_wrapper(
            'langchain_core.retrievers',
            'BaseRetriever.aget_relevant_documents',
            generic_patch(
                'BaseRetriever.aget_relevant_documents', 'retriever', tracer, version)
        )

        # Prompt
        wrap_function_wrapper(
            'langchain_core.prompts.chat',
            'ChatPromptTemplate.from_template',
            generic_patch(
                'ChatPromptTemplate.from_template', 'chatprompt', tracer, version)
        )

        # Runnable
        wrap_function_wrapper(
            'langchain_core.runnables.base',
            'RunnableParallel.invoke',
            runnable_patch(
                'RunnableParallel.invoke', 'runnableparallel', tracer, version)
        )

        wrap_function_wrapper(
            'langchain_core.runnables.passthrough',
            'RunnablePassthrough.invoke',
            runnable_patch(
                'RunnablePassthrough.invoke', 'runnablepassthrough', tracer, version)
        )

        # Output Parsers
        wrap_function_wrapper(
            'langchain_core.output_parsers.string',
            'StrOutputParser.parse',
            runnable_patch(
                'StrOutputParser.parse', 'stroutputparser', tracer, version)
        )

        wrap_function_wrapper(
            'langchain_core.output_parsers.json',
            'JsonOutputParser.parse',
            runnable_patch(
                'JsonOutputParser.parse', 'jsonoutputparser', tracer, version)
        )

        wrap_function_wrapper(
            'langchain_core.output_parsers.list',
            'ListOutputParser.parse',
            runnable_patch(
                'ListOutputParser.parse', 'listoutputparser', tracer, version)
        )

        wrap_function_wrapper(
            'langchain_core.output_parsers.xml',
            'XMLOutputParser.parse',
            runnable_patch(
                'XMLOutputParser.parse', 'xmloutputparser', tracer, version)
        )

    def _uninstrument(self, **kwargs):
        print(kwargs)
