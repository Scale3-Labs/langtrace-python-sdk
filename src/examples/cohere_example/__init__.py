from examples.cohere_example.chat import chat_comp
from examples.cohere_example.chatv2 import chat_v2
from examples.cohere_example.chat_streamv2 import chat_stream_v2
from examples.cohere_example.chat_stream import chat_stream
from examples.cohere_example.tools import tool_calling
from examples.cohere_example.embed import embed
from examples.cohere_example.rerank import rerank
from examples.cohere_example.rerankv2 import rerank_v2
from langtrace_python_sdk import with_langtrace_root_span


class CohereRunner:

    @with_langtrace_root_span("Cohere")
    def run(self):
        chat_v2()
        chat_stream_v2()
        chat_comp()
        chat_stream()
        tool_calling()
        embed()
        rerank()
        rerank_v2()
