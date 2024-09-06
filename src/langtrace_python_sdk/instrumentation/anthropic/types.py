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

from typing import Dict, List, Optional, Iterator, TypedDict


class MessagesCreateKwargs(TypedDict, total=False):
    system: Optional[str]
    messages: List[Dict[str, str]]


class Usage:
    input_tokens: int
    output_tokens: int

    def __init__(self, input_tokens: int, output_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class Message:
    def __init__(
        self,
        id: str,
        model: Optional[str],
        usage: Optional[Usage],
    ):
        self.id = id
        self.model = model
        self.usage = usage

    model: Optional[str]
    usage: Optional[Usage]


class Delta:
    text: Optional[str]

    def __init__(
        self,
        text: Optional[str],
    ):
        self.text = text


class Chunk:
    message: Message
    delta: Delta

    def __init__(
        self,
        message: Message,
        delta: Delta,
    ):
        self.message = message
        self.delta = delta


class ContentItem:
    role: str
    text: str
    type: str

    def __init__(self, role: str, content: str, text: str, type: str):
        self.role = role
        self.content = content
        self.text = text
        self.type = type


class ResultType:
    model: Optional[str]
    role: Optional[str]
    content: List[ContentItem]
    system_fingerprint: Optional[str]
    usage: Optional[Usage]

    def __init__(
        self,
        model: Optional[str],
        role: Optional[str],
        content: Optional[List[ContentItem]],
        system_fingerprint: Optional[str],
        usage: Optional[Usage],
    ):
        self.model = model
        self.role = role
        self.content = content if content is not None else []
        self.system_fingerprint = system_fingerprint
        self.usage = usage


# The result would be an iterator that yields these Chunk objects
StreamingResult = Iterator[Chunk]
