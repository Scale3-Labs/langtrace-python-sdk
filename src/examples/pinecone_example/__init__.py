from langtrace_python_sdk import with_langtrace_root_span


class PineconeRunner:
    @with_langtrace_root_span("Pinecone")
    def run(self):
        from .basic import basic as basic_app

        basic_app()
