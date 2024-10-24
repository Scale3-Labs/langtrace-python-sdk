from examples.awsbedrock_examples.converse import use_converse
from langtrace_python_sdk import langtrace, with_langtrace_root_span

langtrace.init()


class AWSBedrockRunner:
    @with_langtrace_root_span("AWS_Bedrock")
    def run(self):
        use_converse()
