import os
import autogen
from langtrace_python_sdk import langtrace
from typing import Dict, Optional, Union, List
from autogen.agentchat.conversable_agent import ConversableAgent
from functools import wraps

# Initialize langtrace
langtrace.init(
    api_key='967b06c4d1858a7e64e58de44708d89e84f8c96a69b20f7276bcb34a7ce495af',
    write_spans_to_console=True,
    api_host="http://localhost:3000/api/trace"
)

def trace_method(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with langtrace.start_span(f"{self.name}_{func.__name__}") as span:
            span.set_attribute("agent_name", self.name)
            span.set_attribute("method_name", func.__name__)
            result = func(self, *args, **kwargs)
            if isinstance(result, dict):
                span.set_attribute("response_type", "dict")
                span.set_attribute("content_length", len(str(result.get("content", ""))))
            elif isinstance(result, str):
                span.set_attribute("response_type", "str")
                span.set_attribute("content_length", len(result))
            return result
    return wrapper

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

    @trace_method
    def generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[autogen.Agent] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """Override generate_reply for mock responses"""
        if not messages:
            return None

        last_message = messages[-1].get("content", "")

        if "Write a Python function" in last_message:
            self.conversation_id += 1
            return {
                "content": "Here's a Python function to calculate Fibonacci sequence:\n\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib",
                "role": "assistant",
                "conversation_id": self.conversation_id
            }
        elif self.name == "User":
            return "Thanks! That's exactly what I needed."

        return None

# Create agents
user = MockAgent(
    name="User",
    system_message="A human user who needs help with coding tasks."
)

assistant = MockAgent(
    name="Assistant",
    system_message="A helpful coding assistant.",
    is_termination_msg=False  # Changed to False to allow conversation to continue
)

# Start the conversation
with langtrace.start_span("mock_conversation") as conversation_span:
    conversation_span.set_attribute("conversation_type", "fibonacci_example")
    user.initiate_chat(
        assistant,
        message="Write a Python function to calculate the Fibonacci sequence."
    )
