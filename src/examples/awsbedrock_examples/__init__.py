from examples.awsbedrock_examples.converse import (
    use_converse_stream,
    use_converse,
    use_invoke_model_anthropic,
    use_invoke_model_cohere,
    use_invoke_model_amazon,
)
from langtrace_python_sdk import langtrace, with_langtrace_root_span


class AWSBedrockRunner:
    @with_langtrace_root_span("AWS_Bedrock")
    def run(self):

        use_converse_stream()
        use_converse()
        use_invoke_model_anthropic()
        use_invoke_model_cohere()
        use_invoke_model_amazon()
