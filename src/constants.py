
TRACE_NAMESPACES = {
    "OPENAI": "Langtrace OpenAI SDK",
    "PINECONE": "Langtrace Pinecone SDK"
}

# TODO: Add more models
# https://github.com/dqbd/tiktoken/blob/74c147e19584a3a1acea0c8e0da4d39415cd33e0/wasm/src/lib.rs#L328
'''
TIKTOKEN_MODEL_MAPPING = {
    "gpt-4": TiktokenEncoding.cl100k_base,
    "gpt-4-32k": TiktokenEncoding.cl100k_base,
    "gpt-4-0125-preview": TiktokenEncoding.cl100k_base,
    "gpt-4-1106-preview": TiktokenEncoding.cl100k_base,
    "gpt-4-1106-vision-preview": TiktokenEncoding.cl100k_base
}
'''
SERVICE_PROVIDERS = {
    "OPENAI": "OpenAI",
    "LANGCHAIN": "Langchain",
    "PINECONE": "Pinecone"
}
