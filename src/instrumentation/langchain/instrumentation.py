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

        # Retriever
        wrap_function_wrapper(
            'langchain_core.retrievers',
            'BaseRetriever.get_relevant_documents',
            generic_patch(
                tracer, 'BaseRetriever.get_relevant_documents', 'retriever')
        )

        wrap_function_wrapper(
            'langchain_core.retrievers',
            'BaseRetriever.aget_relevant_documents',
            generic_patch(
                tracer, 'BaseRetriever.aget_relevant_documents', 'retriever')
        )

        # Prompt
        wrap_function_wrapper(
            'langchain_core.prompts.chat',
            'ChatPromptTemplate.from_template',
            generic_patch(
                tracer, 'ChatPromptTemplate.from_template', 'chatprompt')
        )

        # Runnable
        wrap_function_wrapper(
            'langchain_core.runnables.base',
            'RunnableParallel.invoke',
            runnable_patch(
                tracer, 'RunnableParallel.invoke', 'runnableparallel')
        )

        wrap_function_wrapper(
            'langchain_core.runnables.passthrough',
            'RunnablePassthrough.invoke',
            runnable_patch(
                tracer, 'RunnablePassthrough.invoke', 'runnablepassthrough')
        )

        # Output Parsers
        wrap_function_wrapper(
            'langchain_core.output_parsers.string',
            'StrOutputParser.parse',
            runnable_patch(
                tracer, 'StrOutputParser.parse', 'stroutputparser')
        )

        wrap_function_wrapper(
            'langchain_core.output_parsers.json',
            'JsonOutputParser.parse',
            runnable_patch(
                tracer, 'JsonOutputParser.parse', 'jsonoutputparser')
        )

        wrap_function_wrapper(
            'langchain_core.output_parsers.list',
            'ListOutputParser.parse',
            runnable_patch(
                tracer, 'ListOutputParser.parse', 'listoutputparser')
        )

        wrap_function_wrapper(
            'langchain_core.output_parsers.xml',
            'XMLOutputParser.parse',
            runnable_patch(
                tracer, 'XMLOutputParser.parse', 'xmloutputparser')
        )

    def _uninstrument(self, **kwargs):
        print(kwargs)
