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
    system: str
    messages: List[Dict[str, str]]

class Usage(TypedDict, total=True):
    input_tokens: int
    output_tokens: int

class Message(TypedDict, total=True):
    model: Optional[str]
    usage: Optional[Usage]

class Delta(TypedDict, total=True):
    text: Optional[str]

class Chunk(TypedDict, total=True):
    message: Message
    delta: Delta

class ContentItem(TypedDict, total=False):
    role: str
    content: str
    text: str
    type: str

class ResultType(TypedDict, total=True):
    model: Optional[str]
    role: Optional[str]
    content: List[ContentItem]
    system_fingerprint: Optional[str]
    usage: Optional[Usage]

# The result would be an iterator that yields these Chunk objects
StreamingResult = Iterator[Chunk]