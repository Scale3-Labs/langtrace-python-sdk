from langtrace_python_sdk import langtrace
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
import re
import json
from openai import OpenAI
import os

load_dotenv()

langtrace.init()
openai_client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY"),
)
client = Cerebras()


def openai_cerebras_example(stream=False):
    completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Why is fast inference important?",
            }
        ],
        model="llama3.1-8b",
        stream=stream,
    )

    if stream:
        for chunk in completion:
            print(chunk)
    else:
        return completion


def completion_example(stream=False):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Why is fast inference important?",
            }
        ],
        model="llama3.1-8b",
        stream=stream,
    )

    if stream:
        for chunk in completion:
            print(chunk)
    else:
        return completion


def completion_with_tools_example(stream=False):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to a calculator. Use the calculator tool to compute mathematical expressions when needed.",
        },
        {"role": "user", "content": "What's the result of 15 multiplied by 7?"},
    ]

    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=messages,
        tools=tools,
        stream=stream,
    )

    if stream:
        # Handle streaming response
        full_content = ""
        for chunk in response:
            if chunk.choices[0].delta.tool_calls:
                tool_call = chunk.choices[0].delta.tool_calls[0]
                if hasattr(tool_call, "function"):
                    if tool_call.function.name == "calculate":
                        arguments = json.loads(tool_call.function.arguments)
                        result = calculate(arguments["expression"])
                        print(f"Calculation result: {result}")

                        # Get final response with calculation result
                        messages.append(
                            {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "function": {
                                            "name": "calculate",
                                            "arguments": tool_call.function.arguments,
                                        },
                                        "id": tool_call.id,
                                        "type": "function",
                                    }
                                ],
                            }
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_call.id,
                            }
                        )

                        final_response = client.chat.completions.create(
                            model="llama3.1-70b", messages=messages, stream=True
                        )

                        for final_chunk in final_response:
                            if final_chunk.choices[0].delta.content:
                                print(final_chunk.choices[0].delta.content, end="")
            elif chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
                full_content += chunk.choices[0].delta.content
    else:
        # Handle non-streaming response
        choice = response.choices[0].message
        if choice.tool_calls:
            function_call = choice.tool_calls[0].function
            if function_call.name == "calculate":
                arguments = json.loads(function_call.arguments)
                result = calculate(arguments["expression"])
                print(f"Calculation result: {result}")

                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "calculate",
                                    "arguments": function_call.arguments,
                                },
                                "id": choice.tool_calls[0].id,
                                "type": "function",
                            }
                        ],
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": choice.tool_calls[0].id,
                    }
                )

                final_response = client.chat.completions.create(
                    model="llama3.1-70b",
                    messages=messages,
                )

                if final_response:
                    print(final_response.choices[0].message.content)
                else:
                    print("No final response received")
        else:
            print("Unexpected response from the model")


def calculate(expression):
    expression = re.sub(r"[^0-9+\-*/().]", "", expression)

    try:
        result = eval(expression)
        return str(result)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError):
        return "Error: Invalid expression"


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "A calculator tool that can perform basic arithmetic operations. Use this when you need to compute mathematical expressions or solve numerical problems.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]
