import asyncio
from examples.mistral_example.complete import chat_complete
from examples.mistral_example.complete_async import complete_async
from examples.mistral_example.embeddings import embeddings_create
from langtrace_python_sdk import langtrace, with_langtrace_root_span

langtrace.init()

class MistralRunner:
    @with_langtrace_root_span("Mistral")
    def run(self):
        chat_complete()
        asyncio.run(complete_async())
        embeddings_create()
