from typing import List, Literal, TypeVar, TypedDict, Union
from enum import Enum


class InstrumentationType(Enum):
    ANTHROPIC = "anthropic"
    AUTOGEN = "autogen"
    CHROMADB = "chromadb"
    COHERE = "cohere"
    CREW_AI = "crewai"
    CREWAI = "crewai"
    DSPY = "dspy-ai"
    EMBEDCHAIN = "embedchain"
    GEMINI = "google-generativeai"
    GOOGLE_CLOUD_AI_PLATFORM = "google-cloud-aiplatform"
    GOOGLE_GENERATIVEAI = "google-generativeai"
    GROQ = "groq"
    LANGCHAIN = "langchain"
    LANGCHAIN_COMMUNITY = "langchain-community"
    LANGCHAIN_CORE = "langchain-core"
    LANGGRAPH = "langgraph"
    LITELLM = "litellm"
    LLAMAINDEX = "llama-index"
    MISTRAL = "mistral"
    MISTRALAI = "mistralai"
    OLLAMA = "ollama"
    OPENAI = "openai"
    PINECONE = "pinecone-client"
    QDRANT = "qdrant"
    SQLALCHEMY = "sqlalchemy"
    VERTEXAI = "vertexai"
    WEAVIATE = "weaviate"
    AWS_BEDROCK = "boto3"

    @staticmethod
    def from_string(value: str):
        try:
            return InstrumentationType[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid value for InstrumentationType: {value}")


class DisableInstrumentations(TypedDict, total=False):
    all_except: List[InstrumentationType]
    only: List[InstrumentationType]


class VendorMethods(TypedDict):
    PineconeMethods = Literal[
        "pinecone.index.upsert", "pinecone.index.query", "pinecone.index.delete"
    ]
    AnthropicMethods = Literal["anthropic.messages.create"]
    GroqMethods = Literal["groq.chat.completions.create"]
    OpenaiMethods = Literal[
        "openai.chat.completions.create",
        "openai.embeddings.create",
        "openai.images.generate",
        "openai.images.edit",
    ]
    MistralMethods = Literal[
        "mistral.chat.complete",
        "mistral.chat.stream",
        "mistral.embeddings.create",
    ]

    AwsBedrockMethods = Literal[
        "aws_bedrock.converse",
        "aws_bedrock.converse_stream",
    ]

    ChromadbMethods = Literal[
        "chromadb.collection.add",
        "chromadb.collection.query",
        "chromadb.collection.delete",
        "chromadb.collection.peek",
        "chromadb.collection.update",
        "chromadb.collection.upsert",
        "chromadb.collection.modify",
        "chromadb.collection.count",
    ]
    QdrantMethods = Literal[
        "qdrantdb.add",
        "qdrantdb.get_collection",
        "qdrantdb.get_collections",
        "qdrantdb.query",
        "qdrantdb.query_batch",
        "qdrantdb.delete",
        "qdrantdb.discover",
        "qdrantdb.discover_batch",
        "qdrantdb.recommend",
        "qdrantdb.recommend_batch",
        "qdrantdb.retrieve",
        "qdrantdb.search",
        "qdrantdb.search_batch",
        "qdrantdb.upsert",
        "qdrantdb.count",
        "qdrantdb.update_collection",
        "qdrantdb.update_vectors",
    ]

    CohereMethods = Literal[
        "cohere.client.chat",
        "cohere.client.embed",
        "cohere.client.rerank",
        "cohere.client.chat_stream",
    ]

    LlamaIndexMethods = Literal[
        "llamaindex.OpenAI.chat",
        "llamaindex.RetrieverQueryEngine.query",
        "llamaindex.VectorIndexRetriever.retrieve",
        "llamaindex.SimpleVectorStore.query",
        "llamaindex.RetrieverQueryEngine.retrieve",
    ]


class InstrumentationMethods(TypedDict):
    open_ai: List[VendorMethods.OpenaiMethods]
    groq: List[VendorMethods.GroqMethods]
    mistral: List[VendorMethods.MistralMethods]
    aws_bedrock: List[VendorMethods.AwsBedrockMethods]
    pinecone: List[VendorMethods.PineconeMethods]
    llamaindex: List[VendorMethods.LlamaIndexMethods]
    chromadb: List[VendorMethods.ChromadbMethods]
    qdrant: List[VendorMethods.QdrantMethods]
    langchain: List[str]
    langchain_core: List[str]
    langchain_community: List[str]
    langgraph: List[str]
    anthropic: List[VendorMethods.AnthropicMethods]
    cohere: List[VendorMethods.CohereMethods]
    weaviate: List[str]


_T = TypeVar("_T")


class NotGiven:
    """
    A sentinel singleton class used to distinguish omitted keyword arguments
    from those passed in with the value None (which may have different behavior).

    For example:

    ```py
    def get(timeout: Union[int, NotGiven, None] = NotGiven()) -> Response:
        ...


    get(timeout=1)  # 1s timeout
    get(timeout=None)  # No timeout
    get()  # Default timeout behavior, which may not be statically known at the method definition.
    ```
    """

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NotGivenOr = Union[_T, NotGiven]
NOT_GIVEN = NotGiven()
