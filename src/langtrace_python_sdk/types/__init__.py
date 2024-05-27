from typing import List, TypedDict
from enum import Enum


class InstrumentationType(Enum):
    OPENAI = "openai"
    COHERE = "cohere"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    PINECONE = "pinecone"
    LLAMAINDEX = "llamaindex"
    CHROMADB = "chromadb"
    QDRANT = "qdrant"
    LANGCHAIN = "langchain"
    LANGCHAIN_CORE = "langchain_core"
    LANGCHAIN_COMMUNITY = "langchain_community"
    LANGGRAPH = "langgraph"
    WEAVIATE = "weaviate"

    @staticmethod
    def from_string(value: str):
        try:
            return InstrumentationType[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid value for InstrumentationType: {value}")


class DisableInstrumentations(TypedDict, total=False):
    all_except: List[InstrumentationType]
    only: List[InstrumentationType]
