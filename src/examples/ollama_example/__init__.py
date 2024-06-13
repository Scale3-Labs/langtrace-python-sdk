from .basic import basic as basic_app, async_basic, generate

import asyncio


class OllamaRunner:
    def run(self):
        basic_app()
        generate()
        asyncio.run(async_basic())
