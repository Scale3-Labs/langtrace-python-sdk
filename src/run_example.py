from colorama import Fore

ENABLED_EXAMPLES = {
    "anthropic": False,
    "chroma": False,
    "cohere": False,
    "fastapi": False,
    "langchain": False,
    "llamaindex": False,
    "hiveagent": False,
    "openai": False,
    "perplexity": False,
    "pinecone": False,
    "qdrant": False,
    "weaviate": False,
    "ollama": False,
    "groq": False,
    "vertexai": False,
    "gemini": True,
}

if ENABLED_EXAMPLES["anthropic"]:
    from examples.anthropic_example import AnthropicRunner

    print(Fore.BLUE + "Running Anthropic example" + Fore.RESET)
    AnthropicRunner().run()

if ENABLED_EXAMPLES["chroma"]:
    from examples.chroma_example import ChromaRunner

    print(Fore.BLUE + "Running Chroma example" + Fore.RESET)
    ChromaRunner().run()

if ENABLED_EXAMPLES["cohere"]:
    from examples.cohere_example import CohereRunner

    print(Fore.BLUE + "Running Cohere example" + Fore.RESET)
    CohereRunner().run()

if ENABLED_EXAMPLES["fastapi"]:
    from examples.fastapi_example import FastAPIRunner

    print(Fore.BLUE + "Running FastAPI example" + Fore.RESET)
    FastAPIRunner().run()

if ENABLED_EXAMPLES["langchain"]:
    from examples.langchain_example import LangChainRunner

    print(Fore.BLUE + "Running LangChain example" + Fore.RESET)
    LangChainRunner().run()

if ENABLED_EXAMPLES["llamaindex"]:
    from examples.llamaindex_example import LlamaIndexRunner

    print(Fore.BLUE + "Running LlamaIndex example" + Fore.RESET)
    LlamaIndexRunner().run()

if ENABLED_EXAMPLES["openai"]:
    from examples.openai_example import OpenAIRunner

    print(Fore.BLUE + "Running OpenAI example" + Fore.RESET)
    OpenAIRunner().run()

if ENABLED_EXAMPLES["pinecone"]:
    from examples.pinecone_example import PineconeRunner

    print(Fore.BLUE + "Running Pinecone example" + Fore.RESET)
    PineconeRunner().run()

if ENABLED_EXAMPLES["qdrant"]:
    from examples.qdrant_example import QdrantRunner

    print(Fore.BLUE + "Running Qdrant example" + Fore.RESET)
    QdrantRunner().run()

if ENABLED_EXAMPLES["weaviate"]:
    from examples.weaviate_example import WeaviateRunner

    print(Fore.BLUE + "Running Weaviate example" + Fore.RESET)
    WeaviateRunner().run()

if ENABLED_EXAMPLES["ollama"]:
    from examples.ollama_example import OllamaRunner

    print(Fore.BLUE + "Running Ollama example" + Fore.RESET)
    OllamaRunner().run()

if ENABLED_EXAMPLES["groq"]:
    from examples.langchain_example import GroqRunner

    print(Fore.BLUE + "Running Groq example" + Fore.RESET)
    GroqRunner().run()


if ENABLED_EXAMPLES["vertexai"]:
    from examples.vertexai_example import VertexAIRunner

    print(Fore.BLUE + "Running Vertexai example" + Fore.RESET)
    VertexAIRunner().run()

if ENABLED_EXAMPLES["gemini"]:
    from examples.gemini_example import GeminiRunner

    print(Fore.BLUE + "Running Gemini example" + Fore.RESET)
    GeminiRunner().run()
