import os
import autogen
from langtrace_python_sdk import langtrace
from typing import Dict, Optional, Union, List
from autogen.agentchat.conversable_agent import ConversableAgent

# Initialize langtrace
langtrace.init(
    api_key='967b06c4d1858a7e64e58de44708d89e84f8c96a69b20f7276bcb34a7ce495af',
    write_spans_to_console=True,
    endpoint="http://localhost:3000"
)

class MockAgent(ConversableAgent):
    def __init__(
        self,
        name: str,
        system_message: Optional[str] = "Mock agent for testing",
        is_termination_msg: Optional[bool] = False,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )
        self.is_termination_msg = is_termination_msg
        self.conversation_id = 0

    def generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[autogen.Agent] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """Override generate_reply for mock responses"""
        if not messages:
            return None

        if self.is_termination_msg:
            return None

        if "Write a Python function" in messages[-1].get("content", ""):
            self.conversation_id += 1
            return {
                "content": "Here's a Python function to calculate Fibonacci sequence:\n\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib",
                "role": "assistant",
                "conversation_id": self.conversation_id
            }
        return None

# Create agents
user = MockAgent(
    name="User",
    system_message="A human user who needs help with coding tasks."
)

assistant = MockAgent(
    name="Assistant",
    system_message="A helpful coding assistant.",
    is_termination_msg=True
)

# Start the conversation
user.initiate_chat(
    assistant,
    message="Write a Python function to calculate the Fibonacci sequence."
)
