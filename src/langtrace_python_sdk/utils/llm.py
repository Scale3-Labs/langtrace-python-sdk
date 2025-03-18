"""
Copyright (c) 2024 Scale3 Labs

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Dict, Union
from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.utils import set_span_attribute
from langtrace_python_sdk.types import NOT_GIVEN
from tiktoken import get_encoding, list_encoding_names

from langtrace_python_sdk.constants.instrumentation.common import (
    LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY,
    TIKTOKEN_MODEL_MAPPING,
)
from langtrace_python_sdk.constants.instrumentation.openai import OPENAI_COST_TABLE
from langtrace.trace_attributes import SpanAttributes
from importlib_metadata import version as v
import json
from opentelemetry import baggage
from opentelemetry.trace import Span
from opentelemetry.trace.status import StatusCode

import os


def get_span_name(operation_name):
    extra_attributes = get_extra_attributes()
    if extra_attributes is not None and "langtrace.span.name" in extra_attributes:
        return f'{operation_name}-{extra_attributes["langtrace.span.name"]}'
    return operation_name


def estimate_tokens(prompt):
    """
    Estimate the number of tokens in a prompt."""
    if prompt and len(prompt) > 0:
        # Simplified token estimation: count the words.
        return len([word for word in prompt.split() if word])
    return 0


def set_event_completion_chunk(span: Span, chunk):
    enabled = os.environ.get("TRACE_PROMPT_COMPLETION_DATA", "true")
    if enabled.lower() == "false":
        return
    span.add_event(
        name=SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK,
        attributes={
            SpanAttributes.LLM_CONTENT_COMPLETION_CHUNK: json.dumps(chunk),
        },
    )


def estimate_tokens_using_tiktoken(prompt, model):
    """
    Estimate the number of tokens in a prompt using tiktoken."""
    encoding = get_encoding(model)
    tokens = encoding.encode(prompt)
    return len(tokens)


def calculate_prompt_tokens(prompt_content, model):
    """
    Calculate the number of tokens in a prompt. If the model is supported by tiktoken, use it for the estimation.
    """
    try:
        tiktoken_model = TIKTOKEN_MODEL_MAPPING[model]
        return estimate_tokens_using_tiktoken(prompt_content, tiktoken_model)
    except Exception:
        return estimate_tokens(prompt_content)  # Fallback method


def calculate_price_from_usage(model, usage):
    """
    Calculate the price of a model based on its usage."""
    cost_table = OPENAI_COST_TABLE.get(model)
    if cost_table:
        return (
            cost_table["input"] * usage["prompt_tokens"]
            + cost_table["output"] * usage["completion_tokens"]
        ) / 1000
    return 0


def convert_mistral_messages_to_serializable(mistral_messages):
    serializable_messages = []

    try:
        for message in mistral_messages:
            serializable_message = {"role": message.role}

            # Handle content
            if hasattr(message, "content"):
                serializable_message["content"] = message.content

            # Handle tool_calls
            if hasattr(message, "tool_calls") and message.tool_calls is not None:
                serializable_tool_calls = []

                for tool_call in message.tool_calls:
                    serializable_tool_call = {}

                    # Handle id, type, and index
                    if hasattr(tool_call, "id"):
                        serializable_tool_call["id"] = tool_call.id
                    if hasattr(tool_call, "type"):
                        serializable_tool_call["type"] = tool_call.type
                    if hasattr(tool_call, "index"):
                        serializable_tool_call["index"] = tool_call.index

                    # Handle function
                    if hasattr(tool_call, "function"):
                        function_call = tool_call.function
                        serializable_function = {}

                        if hasattr(function_call, "name"):
                            serializable_function["name"] = function_call.name
                        if hasattr(function_call, "arguments"):
                            serializable_function["arguments"] = function_call.arguments

                        serializable_tool_call["function"] = serializable_function

                    serializable_tool_calls.append(serializable_tool_call)

                serializable_message["tool_calls"] = serializable_tool_calls

            # Handle tool_call_id for tool messages
            if hasattr(message, "tool_call_id"):
                serializable_message["tool_call_id"] = message.tool_call_id

            serializable_messages.append(serializable_message)
    except Exception as e:
        pass

    return serializable_messages


def convert_gemini_messages_to_serializable(formatted_messages, system_message=None):
    """
    Converts Gemini-formatted messages back to a JSON serializable format.

    Args:
        formatted_messages: The formatted messages from Gemini.
        system_message (str, optional): System message content.

    Returns:
        List[dict]: JSON serializable list of message dictionaries.
    """
    serializable_messages = []

    try:
        # Add system message if present
        if system_message:
            serializable_messages.append({"role": "system", "content": system_message})

        for message_item in formatted_messages:
            # Handle the case where the item is a dict with 'role' and 'content' keys
            if (
                isinstance(message_item, dict)
                and "role" in message_item
                and "content" in message_item
            ):
                role = message_item["role"]
                content_value = message_item["content"]

                # Initialize our serializable message
                serializable_message = {"role": role}

                # If content is a list of Content objects
                if isinstance(content_value, list) and len(content_value) > 0:
                    for content_obj in content_value:
                        # Process each Content object
                        if hasattr(content_obj, "parts") and hasattr(
                            content_obj, "role"
                        ):
                            parts = content_obj.parts

                            # Extract text from parts
                            text_parts = []
                            for part in parts:
                                if hasattr(part, "text") and part.text:
                                    text_parts.append(part.text)

                            if text_parts:
                                serializable_message["content"] = " ".join(text_parts)

                            # Here you can add additional processing for other part types
                            # like function_call, function_response, inline_data, etc.
                            # Similar to the previous implementation

                # If content is a string or already a primitive type
                elif (
                    isinstance(content_value, (str, int, float, bool))
                    or content_value is None
                ):
                    serializable_message["content"] = content_value

                # Add the processed message to our list
                serializable_messages.append(serializable_message)

            # Handle the case where the item is a Content object directly
            elif hasattr(message_item, "role") and hasattr(message_item, "parts"):
                # This is the case from the previous implementation
                # Process a Content object directly
                serializable_message = {"role": message_item.role}

                parts = message_item.parts
                text_parts = []

                for part in parts:
                    if hasattr(part, "text") and part.text:
                        text_parts.append(part.text)

                if text_parts:
                    serializable_message["content"] = " ".join(text_parts)

                serializable_messages.append(serializable_message)
    except Exception as e:
        pass

    return serializable_messages


def get_langtrace_attributes(version, service_provider, vendor_type="llm"):
    return {
        SpanAttributes.LANGTRACE_SDK_NAME: LANGTRACE_SDK_NAME,
        SpanAttributes.LANGTRACE_VERSION: v(LANGTRACE_SDK_NAME),
        SpanAttributes.LANGTRACE_SERVICE_VERSION: version,
        SpanAttributes.LANGTRACE_SERVICE_NAME: service_provider,
        SpanAttributes.LANGTRACE_SERVICE_TYPE: vendor_type,
        SpanAttributes.LLM_SYSTEM: service_provider.lower(),
    }


def get_llm_request_attributes(kwargs, prompts=None, model=None, operation_name="chat"):

    user = kwargs.get("user", None)
    if prompts is None:
        prompts = (
            [{"role": user or "user", "content": kwargs.get("prompt")}]
            if "prompt" in kwargs
            else None
        )
    top_k = (
        kwargs.get("n", None)
        or kwargs.get("k", None)
        or kwargs.get("top_k", None)
        or kwargs.get("top_n", None)
    )

    try:
        prompts = json.dumps(prompts) if prompts else None
    except Exception as e:
        if "is not JSON serializable" in str(e):
            # check model
            if kwargs.get("model") is not None:
                if kwargs.get("model").startswith("gemini"):
                    prompts = json.dumps(
                        convert_gemini_messages_to_serializable(prompts)
                    )
                elif kwargs.get("model").startswith("mistral"):
                    prompts = json.dumps(
                        convert_mistral_messages_to_serializable(prompts)
                    )
                else:
                    prompts = "[]"
            else:
                prompts = "[]"
        else:
            prompts = "[]"

    top_p = kwargs.get("p", None) or kwargs.get("top_p", None)
    tools = kwargs.get("tools", None)
    tool_choice = kwargs.get("tool_choice", None)
    return {
        SpanAttributes.LLM_OPERATION_NAME: operation_name,
        SpanAttributes.LLM_REQUEST_MODEL: model
        or kwargs.get("model")
        or "gpt-3.5-turbo",
        SpanAttributes.LLM_IS_STREAMING: kwargs.get("stream"),
        SpanAttributes.LLM_REQUEST_TEMPERATURE: kwargs.get("temperature"),
        SpanAttributes.LLM_TOP_K: top_k,
        SpanAttributes.LLM_PROMPTS: prompts if prompts else None,
        SpanAttributes.LLM_USER: user,
        SpanAttributes.LLM_REQUEST_TOP_P: top_p,
        SpanAttributes.LLM_REQUEST_MAX_TOKENS: kwargs.get("max_tokens"),
        SpanAttributes.LLM_SYSTEM_FINGERPRINT: kwargs.get("system_fingerprint"),
        SpanAttributes.LLM_PRESENCE_PENALTY: kwargs.get("presence_penalty"),
        SpanAttributes.LLM_FREQUENCY_PENALTY: kwargs.get("frequency_penalty"),
        SpanAttributes.LLM_REQUEST_SEED: kwargs.get("seed"),
        SpanAttributes.LLM_TOOLS: json.dumps(tools) if tools else None,
        SpanAttributes.LLM_TOOL_CHOICE: (
            json.dumps(tool_choice) if tool_choice else None
        ),
        SpanAttributes.LLM_REQUEST_LOGPROPS: kwargs.get("logprobs"),
        SpanAttributes.LLM_REQUEST_LOGITBIAS: kwargs.get("logit_bias"),
        SpanAttributes.LLM_REQUEST_TOP_LOGPROPS: kwargs.get("top_logprobs"),
    }


def get_extra_attributes() -> Union[Dict[str, Any], object]:
    extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
    return extra_attributes or {}


def get_llm_url(instance):
    return {
        SpanAttributes.LLM_URL: get_base_url(instance),
    }


def get_base_url(instance):
    base_url = (
        str(instance._client._base_url)
        if hasattr(instance, "_client") and hasattr(instance._client, "_base_url")
        else ""
    )
    return base_url


def is_streaming(kwargs):
    return not (
        kwargs.get("stream") is False
        or kwargs.get("stream") is None
        or kwargs.get("stream") == NOT_GIVEN
    )


def set_usage_attributes(span, usage):
    if usage is None:
        return

    input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
    output_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0

    set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
        input_tokens,
    )

    set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
        output_tokens,
    )

    set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
        input_tokens + output_tokens,
    )

    if "search_units" in usage:
        set_span_attribute(
            span, SpanAttributes.LLM_USAGE_SEARCH_UNITS, usage["search_units"]
        )


def get_tool_calls(item):
    if isinstance(item, dict):
        if "tool_calls" in item and item["tool_calls"] is not None:
            return item["tool_calls"]
        return None

    else:
        if hasattr(item, "tool_calls") and item.tool_calls is not None:
            return item.tool_calls
        return None


def set_event_completion(span: Span, result_content):
    enabled = os.environ.get("TRACE_PROMPT_COMPLETION_DATA", "true")
    if enabled.lower() == "false":
        return

    span.add_event(
        name=SpanAttributes.LLM_CONTENT_COMPLETION,
        attributes={
            SpanAttributes.LLM_COMPLETIONS: json.dumps(result_content),
        },
    )


def set_span_attributes(span: Span, attributes: Any) -> None:
    from pydantic import BaseModel

    attrs = (
        attributes.model_dump(by_alias=True)
        if isinstance(attributes, BaseModel)
        else attributes
    )

    for field, value in attrs.items():
        set_span_attribute(span, field, value)


class StreamWrapper:
    span: Span

    def __init__(
        self, stream, span, prompt_tokens=0, function_call=False, tool_calls=False
    ):
        self.stream = stream
        self.span = span
        self.prompt_tokens = prompt_tokens
        self.function_call = function_call
        self.tool_calls = tool_calls
        self.result_content = []
        self.completion_tokens = 0
        self._span_started = False
        self._response_model = None
        self.setup()

    def setup(self):
        if not self._span_started:
            self._span_started = True

    def cleanup(self):
        if self.completion_tokens == 0:
            response_model = "cl100k_base"
            if self._response_model in list_encoding_names():
                response_model = self._response_model
            self.completion_tokens = estimate_tokens_using_tiktoken(
                "".join(self.result_content), response_model
            )
        if self._span_started:
            print("SPAAN", self.span)
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_RESPONSE_MODEL,
                self._response_model,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_PROMPT_TOKENS,
                self.prompt_tokens,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_COMPLETION_TOKENS,
                self.completion_tokens,
            )
            set_span_attribute(
                self.span,
                SpanAttributes.LLM_USAGE_TOTAL_TOKENS,
                self.prompt_tokens + self.completion_tokens,
            )
            set_event_completion(
                self.span,
                [
                    {
                        "role": "assistant",
                        "content": "".join(self.result_content),
                    }
                ],
            )
            self.span.set_status(StatusCode.OK)
            self.span.end()
            self._span_started = False

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    async def __aenter__(self):
        self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            chunk = next(self.stream)
            self.process_chunk(chunk)
            return chunk
        except StopIteration:
            self.cleanup()
            raise

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            chunk = await self.stream.__anext__()
            self.process_chunk(chunk)
            return chunk
        except StopAsyncIteration:
            self.cleanup()
            raise StopAsyncIteration

    def set_response_model(self, chunk):
        if self._response_model:
            return

        # OpenAI response model is set on all chunks
        if hasattr(chunk, "model") and chunk.model is not None:
            self._response_model = chunk.model

        # Anthropic response model is set on the first chunk message
        if hasattr(chunk, "message") and chunk.message is not None:
            if hasattr(chunk.message, "model") and chunk.message.model is not None:
                self._response_model = chunk.message.model

    def build_streaming_response(self, chunk):
        content = []
        # OpenAI
        if hasattr(chunk, "choices") and chunk.choices is not None:
            if not self.function_call and not self.tool_calls:
                for choice in chunk.choices:
                    if choice.delta and choice.delta.content is not None:
                        content = [choice.delta.content]
            elif self.function_call:
                for choice in chunk.choices:
                    if (
                        choice.delta
                        and choice.delta.function_call is not None
                        and choice.delta.function_call.arguments is not None
                    ):
                        content = [choice.delta.function_call.arguments]
            elif self.tool_calls:
                for choice in chunk.choices:
                    if choice.delta and choice.delta.tool_calls is not None:
                        toolcalls = choice.delta.tool_calls
                        content = []
                        for tool_call in toolcalls:
                            if (
                                tool_call
                                and tool_call.function is not None
                                and tool_call.function.arguments is not None
                            ):
                                content.append(tool_call.function.arguments)

        # VertexAI
        if hasattr(chunk, "text") and chunk.text is not None:
            content = [chunk.text]

        # CohereV2
        if (
            hasattr(chunk, "delta")
            and chunk.delta is not None
            and hasattr(chunk.delta, "message")
            and chunk.delta.message is not None
            and hasattr(chunk.delta.message, "content")
            and chunk.delta.message.content is not None
            and hasattr(chunk.delta.message.content, "text")
            and chunk.delta.message.content.text is not None
        ):
            content = [chunk.delta.message.content.text]
        # google-cloud-aiplatform
        if hasattr(chunk, "candidates") and chunk.candidates is not None:
            for candidate in chunk.candidates:
                if hasattr(candidate, "content") and candidate.content is not None:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text is not None:
                            content.append(part.text)
        # Anthropic
        if (
            hasattr(chunk, "delta")
            and chunk.delta is not None
            and not hasattr(chunk.delta, "message")
        ):
            content = [chunk.delta.text] if hasattr(chunk.delta, "text") else []
        # OpenAI Responses API
        if hasattr(chunk, "type") and chunk.type == "response.completed":
            content = [chunk.response.output_text]

        if isinstance(chunk, dict):
            if "message" in chunk:
                if "content" in chunk["message"]:
                    content = [chunk["message"]["content"]]
        if content:
            self.result_content.append(content[0])

    def set_usage_attributes(self, chunk):
        # Responses API OpenAI
        if hasattr(chunk, "type") and chunk.type == "response.completed":
            usage = chunk.response.usage
            self.completion_tokens = usage.output_tokens
            self.prompt_tokens = usage.input_tokens
        # Anthropic & OpenAI
        if hasattr(chunk, "type") and chunk.type == "message_start":
            if hasattr(chunk.message, "usage") and chunk.message.usage is not None:
                self.prompt_tokens = chunk.message.usage.input_tokens

        # CohereV2
        if hasattr(chunk, "type") and chunk.type == "message-end":
            if (
                hasattr(chunk, "delta")
                and chunk.delta is not None
                and hasattr(chunk.delta, "usage")
                and chunk.delta.usage is not None
                and hasattr(chunk.delta.usage, "billed_units")
                and chunk.delta.usage.billed_units is not None
            ):
                usage = chunk.delta.usage.billed_units
                self.completion_tokens = int(usage.output_tokens)
                self.prompt_tokens = int(usage.input_tokens)

        if hasattr(chunk, "usage") and chunk.usage is not None:
            if hasattr(chunk.usage, "output_tokens"):
                self.completion_tokens = chunk.usage.output_tokens

            if hasattr(chunk.usage, "prompt_tokens"):
                self.prompt_tokens = chunk.usage.prompt_tokens

            if hasattr(chunk.usage, "completion_tokens"):
                self.completion_tokens = chunk.usage.completion_tokens

        # VertexAI
        if hasattr(chunk, "usage_metadata") and chunk.usage_metadata is not None:
            self.completion_tokens = chunk.usage_metadata.candidates_token_count
            self.prompt_tokens = chunk.usage_metadata.prompt_token_count

        # Ollama
        if isinstance(chunk, dict):
            if "prompt_eval_count" in chunk:
                self.prompt_tokens = chunk["prompt_eval_count"]
            if "eval_count" in chunk:
                self.completion_tokens = chunk["eval_count"]

    def process_chunk(self, chunk):
        # Mistral nests the chunk data under a `data` attribute
        if (
            hasattr(chunk, "data")
            and chunk.data is not None
            and hasattr(chunk.data, "choices")
            and chunk.data.choices is not None
        ):
            chunk = chunk.data

        self.set_response_model(chunk=chunk)
        self.build_streaming_response(chunk=chunk)
        self.set_usage_attributes(chunk=chunk)
