class CerebrasRunner:
    def run(self):
        from .main import completion_example, completion_with_tools_example

        completion_with_tools_example()
        completion_example()
