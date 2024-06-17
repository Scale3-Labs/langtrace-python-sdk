from .basic import chat, async_chat, async_generate, generate, embed, async_embed
from langtrace_python_sdk import with_langtrace_root_span
import asyncio


class OllamaRunner:
    @with_langtrace_root_span("OllamaRunner")
    def run(self):
        chat()
        generate()
        embed()
        asyncio.run(async_chat())
        asyncio.run(async_generate())
        asyncio.run(async_embed())
