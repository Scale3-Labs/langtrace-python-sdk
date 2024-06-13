import json

from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI

from langtrace_python_sdk import langtrace, with_langtrace_root_span

# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(write_spans_to_console=True)

client = AsyncOpenAI()


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "72", "unit": unit}
        )
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def get_current_time(location):
    """Get the current time in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "time": "10"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "time": "72"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "time": "22"})
    else:
        return json.dumps({"location": location, "time": "unknown"})


@with_langtrace_root_span("Run Conversation Streaming")
async def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
        {
            "role": "user",
            "content": "What's the weather like in San Francisco, Tokyo, and Paris?",
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                    },
                    "required": ["location"],
                },
            },
        },
    ]
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        stream=True,
    )

    # For streaming, uncomment the following lines
    tool_call_dict = {}
    tool_calls = []
    id = ""
    name = ""
    arguments = ""
    async for chunk in response:
        if (
            chunk.choices[0].delta is not None
            and chunk.choices[0].delta.tool_calls is not None
        ):
            for choice in chunk.choices:
                for tool_call in choice.delta.tool_calls:
                    if tool_call.id and id != tool_call.id:
                        id = tool_call.id if tool_call.id else ""
                        name = (
                            tool_call.function.name
                            if tool_call.function and tool_call.function.name
                            else ""
                        )
                        tool_call_dict[name] = {
                            "id": id,
                            "function": {"name": name, "arguments": arguments},
                            "type": "function",
                        }
                    arguments += (
                        tool_call.function.arguments
                        if tool_call.function and tool_call.function.arguments
                        else ""
                    )
                if name != "":
                    tool_call_dict[name] = {
                        "id": id,
                        "function": {"name": name, "arguments": arguments},
                        "type": "function",
                    }
    for key, value in tool_call_dict.items():
        tool_calls.append(value)

    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_current_time": get_current_time,
        }  # only one function in this example, but you can have multiple
        # messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call["function"]["arguments"])
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            func_res = json.loads(function_response)
            content = f"Use the below information to answer the user's question: The current weather in {func_res['location']} is {func_res['temperature']} degrees {func_res['unit']}"
            messages.append(
                {"role": "system", "content": content}
            )  # extend conversation with function response
        print(messages)
        second_response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True,
        )  # get a new response from the model where it can see the function response
        result = []
        async for chunk in second_response:
            if chunk.choices[0].delta.content is not None:
                content = [
                    (
                        choice.delta.content
                        if choice.delta and choice.delta.content
                        else ""
                    )
                    for choice in chunk.choices
                ]
                result.append(content[0] if len(content) > 0 else "")
        print("".join(result))
        # return second_response
