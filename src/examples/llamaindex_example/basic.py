from dotenv import find_dotenv, load_dotenv
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

_ = load_dotenv(find_dotenv())


langtrace.init(batch=False, debug_log_to_console=True, write_to_langtrace_cloud=False)


@with_langtrace_root_span()
def basic():
    documents = SimpleDirectoryReader("src/examples/llamaindex_example/data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("What did the author do in college?")
    print(response)
