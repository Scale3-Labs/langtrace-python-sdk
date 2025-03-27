import os
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from neo4j import GraphDatabase
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.llm import OpenAILLM as LLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings as Embeddings
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

langtrace.init()

neo4j_driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))

ex_llm=LLM(
   model_name="gpt-4o-mini",
   model_params={
       "response_format": {"type": "json_object"},
       "temperature": 0
   })

embedder = Embeddings()

@with_langtrace_root_span("run_neo_rag")
async def search():
    # 1. Build KG and Store in Neo4j Database
    kg_builder_pdf = SimpleKGPipeline(
        llm=ex_llm,
        driver=neo4j_driver,
        embedder=embedder,
        from_pdf=True
    )
    await kg_builder_pdf.run_async(file_path='src/examples/neo4j_graphrag_example/data/abramov.pdf')
    
    create_vector_index(neo4j_driver, name="text_embeddings", label="Chunk",
                    embedding_property="embedding", dimensions=1536, similarity_fn="cosine")

    # 2. KG Retriever
    vector_retriever = VectorRetriever(
        neo4j_driver,
        index_name="text_embeddings",
        embedder=embedder
    )

    # 3. GraphRAG Class
    llm = LLM(model_name="gpt-4o")
    rag = GraphRAG(llm=llm, retriever=vector_retriever)

    # 4. Run
    response = rag.search("What did the author do in college?")
    print(response.answer)
