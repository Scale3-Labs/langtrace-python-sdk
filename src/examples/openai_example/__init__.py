from langtrace_python_sdk import with_langtrace_root_span


class OpenAIRunner:
    @with_langtrace_root_span("OpenAI")
    def run(self):
        import asyncio
        from .async_tool_calling_nonstreaming import run_conversation
        from .async_tool_calling_streaming import (
            run_conversation as run_conversation_streaming,
        )
        from .chat_completion import chat_completion as chat_completion_example

        from .embeddings_create import embeddings_create as embeddings_create_example
        from .function_calling import function_calling as function_example
        from .images_edit import image_edit

        asyncio.run(run_conversation())
        asyncio.run(run_conversation_streaming())
        chat_completion_example()
        embeddings_create_example()
        function_example()
        image_edit()
