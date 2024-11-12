class CerebrasRunner:
    def run(self):
        from .main import (
            completion_example,
            completion_with_tools_example,
            openai_cerebras_example,
        )

        completion_with_tools_example()
        completion_example()
        openai_cerebras_example()
