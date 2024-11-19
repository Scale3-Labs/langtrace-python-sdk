import os
import autogen
from langtrace_python_sdk import langtrace
from typing import Dict, Optional, Union
from autogen.agentchat.agent import Agent

# Initialize langtrace
langtrace.init(
    api_key='967b06c4d1858a7e64e58de44708d89e84f8c96a69b20f7276bcb34a7ce495af',
    write_spans_to_console=True,
)

class MockAgent(Agent):
    def __init__(
        self,
        name: str,
        system_message: Optional[str] = "Mock agent for testing",
    ):
        super().__init__(name)
        self._system_message = system_message

    def generate_reply(
        self,
        messages: Optional[Dict] = None,
        sender: Optional[Agent] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """Mock reply generation"""
        if "Write a Python function" in messages[-1].get("content", ""):
            return {
                "content": "Here's a Python function to calculate Fibonacci sequence:\n\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib",
                "role": "assistant"
            }
        return {"content": "I understand your request.", "role": "assistant"}

# Create agents
user = MockAgent(
    name="User",
    system_message="A human user who needs help with coding tasks."
)

assistant = MockAgent(
    name="Assistant",
    system_message="A helpful coding assistant."
)

# Start the conversation
user.initiate_chat(
    assistant,
    message="Write a Python function to calculate the Fibonacci sequence."
)
