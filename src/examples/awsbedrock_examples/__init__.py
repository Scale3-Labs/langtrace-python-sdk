from examples.awsbedrock_examples.converse import use_converse, use_converse_stream
from langtrace_python_sdk import langtrace, with_langtrace_root_span

langtrace.init()

class AWSBedrockRunner:
    @with_langtrace_root_span("AWS_Bedrock")
    def run(self):
        # Standard completion
        print("\nRunning standard completion example...")
        response = use_converse()
        if response:
            content = response.get('output', {}).get('message', {}).get('content', [])
            if content:
                print(f"Response: {content[0].get('text', '')}")

        # Streaming completion
        print("\nRunning streaming completion example...")
        try:
            for chunk in use_converse_stream():
                content = chunk.get('output', {}).get('message', {}).get('content', [])
                if content:
                    print(f"Chunk: {content[0].get('text', '')}", end='', flush=True)
            print("\nStreaming complete!")
        except Exception as e:
            print(f"\nStreaming failed: {e}")
