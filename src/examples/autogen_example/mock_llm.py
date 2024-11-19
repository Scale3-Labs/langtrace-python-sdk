import os
import autogen
from langtrace_python_sdk import langtrace

# Initialize langtrace
langtrace.init(
    write_spans_to_console=True,
)

# Mock LLM config that always returns a fixed response
class MockLLM:
    def create(self, messages, *args, **kwargs):
        return {
            "choices": [{
                "message": {
                    "content": "Here's a Python function to calculate Fibonacci sequence:\n\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib",
                    "role": "assistant"
                }
            }],
            "model": "mock-model",
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "total_tokens": 150
            }
        }

# Configure agents with mock LLM
config_list = [{"model": "mock-model"}]
llm_config = {
    "config_list": config_list,
    "seed": 42,
    "temperature": 0.7,
    "cache_seed": 42,
    "config_list": config_list,
    "timeout": 120,
}

# Create agents
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="A human user who needs help with coding tasks.",
    llm_config=llm_config,
    code_execution_config=False,  # Disable code execution for testing
)

coder = autogen.AssistantAgent(
    name="Coder",
    llm_config=llm_config,
    system_message="Python developer who writes clean code."
)

# Override the create method in the client
coder.client.create = MockLLM().create
user_proxy.client.create = MockLLM().create

# Start the conversation
user_proxy.initiate_chat(
    coder,
    message="Write a Python function to calculate the Fibonacci sequence."
)
