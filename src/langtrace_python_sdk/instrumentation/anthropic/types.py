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