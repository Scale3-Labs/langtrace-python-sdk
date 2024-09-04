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

from typing import Any, Dict, List, Union, Optional, TypedDict


class ContentItem:
    url: str
    revised_prompt: str
    base64: Optional[str]

    def __init__(
        self,
        url: str,
        revised_prompt: str,
        base64: Optional[str],
    ):
        self.url = url
        self.revised_prompt = revised_prompt
        self.base64 = base64


class ToolFunction:
    name: str
    arguments: str

    def __init__(
        self,
        name: str,
        arguments: str,
    ):
        self.name = name
        self.arguments = arguments


class ToolCall:
    id: str
    type: str
    function: ToolFunction

    def __init__(
        self,
        id: str,
        type: str,
        function: ToolFunction,
    ):
        self.id = id
        self.type = type
        self.function = function


class Message:
    role: str
    content: Union[str, List[ContentItem], Dict[str, Any]]
    tool_calls: Optional[List[ToolCall]]

    def __init__(
        self,
        role: str,
        content: Union[str, List[ContentItem], Dict[str, Any]],
        content_filter_results: Optional[Any],
    ):
        self.role = role
        self.content = content
        self.content_filter_results = content_filter_results


class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __init__(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class Choice:
    message: Message
    content_filter_results: Optional[Any]

    def __init__(
        self,
        message: Message,
        content_filter_results: Optional[Any],
    ):
        self.message = message
        self.content_filter_results = content_filter_results


class ResultType:
    model: Optional[str]
    content: List[ContentItem]
    system_fingerprint: Optional[str]
    usage: Optional[Usage]
    choices: Optional[List[Choice]]
    response_format: Optional[str]
    size: Optional[str]
    encoding_format: Optional[str]

    def __init__(
        self,
        model: Optional[str],
        role: Optional[str],
        content: List[ContentItem],
        system_fingerprint: Optional[str],
        usage: Optional[Usage],
        functions: Optional[List[ToolCall]],
        tools: Optional[List[ToolCall]],
        choices: Optional[List[Choice]],
        response_format: Optional[str],
        size: Optional[str],
        encoding_format: Optional[str],
    ):
        self.model = model
        self.role = role
        self.content = content
        self.system_fingerprint = system_fingerprint
        self.usage = usage
        self.functions = functions
        self.tools = tools
        self.choices = choices
        self.response_format = response_format
        self.size = size
        self.encoding_format = encoding_format


class ImagesGenerateKwargs(TypedDict, total=False):
    operation_name: str
    model: Optional[str]
    messages: Optional[List[Message]]
    functions: Optional[List[ToolCall]]
    tools: Optional[List[ToolCall]]
    response_format: Optional[str]
    size: Optional[str]
    encoding_format: Optional[str]


class ImagesEditKwargs(TypedDict, total=False):
    response_format: Optional[str]
    size: Optional[str]


class ChatCompletionsCreateKwargs(TypedDict, total=False):
    model: Optional[str]
    messages: List[Message]
    functions: Optional[List[ToolCall]]
    tools: Optional[List[ToolCall]]


class EmbeddingsCreateKwargs(TypedDict, total=False):
    dimensions: Optional[str]
    input: Union[str, List[str], None]
    encoding_format: Optional[Union[List[str], str]]
