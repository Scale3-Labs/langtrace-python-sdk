from dotenv import find_dotenv, load_dotenv
from init import init
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from utils.with_root_span import with_langtrace_root_span


_ = load_dotenv(find_dotenv())


init()


@with_langtrace_root_span()
def basic():
    documents = SimpleDirectoryReader(
        "src/examples/llamaindex_example/data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("What did the author do in college?")
    print(response)
