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
class ContentItem(TypedDict, total=False):
    url: str
    revised_prompt: str
    base64: Optional[str]  # Only used in images_edit


class Message(TypedDict, total=False):
    role: str
    content: Union[str, List[ContentItem], Dict[str, Any]]
    content_filter_results: Optional[Any]


class ToolFunction(TypedDict, total=False):
    name: str
    arguments: str


class ToolCall(TypedDict, total=False):
    id: str
    type: str
    function: Optional[ToolFunction]


class Usage(TypedDict, total=True):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ResultType(TypedDict, total=True):
    model: Optional[str]
    role: Optional[str]
    content: List[ContentItem]
    system_fingerprint: Optional[str]
    usage: Optional[Usage]


class ImagesGenerateKwargs(TypedDict, total=False):
    operation_name: str
    model: Optional[str]
    messages: Optional[List[Message]]
    functions: Optional[List[ToolCall]]
    tools: Optional[List[ToolCall]]


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

