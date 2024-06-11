from langtrace_python_sdk import with_langtrace_root_span


class LlamaIndexRunner:
    @with_langtrace_root_span("LlamaIndex")
    def run(self):
        from .basic import basic_app
        from .agent import main

        basic_app()
        main()
