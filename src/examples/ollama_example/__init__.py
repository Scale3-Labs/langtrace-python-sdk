from .basic import chat, async_chat, async_generate, generate

import asyncio


class OllamaRunner:
    def run(self):
        chat()
        generate()
        asyncio.run(async_chat())
        asyncio.run(async_generate())
