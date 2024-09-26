from openai import OpenAI
from pgvector.psycopg import register_vector
import psycopg
from langtrace_python_sdk import langtrace

langtrace.init(write_spans_to_console=True)

conn = psycopg.connect(dbname='postgres', autocommit=True, password="mypw", user="postgres", host="localhost")
conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
register_vector(conn)

client = OpenAI()


def setup_db():
    conn.execute('DROP TABLE IF EXISTS documents')
    conn.execute('CREATE TABLE documents (id bigserial PRIMARY KEY, content text, embedding vector(1536))')

    input = [
        'The dog is barking',
        'The cat is purring',
        'The bear is growling'
    ]

    response = client.embeddings.create(input=input, model='text-embedding-3-small')
    embeddings = [v.embedding for v in response.data]

    for content, embedding in zip(input, embeddings):
        conn.execute('INSERT INTO documents (content, embedding) VALUES (%s, %s)', (content, embedding))


def basic_pgvector():
    setup_db()
    document_id = 1
    neighbors = conn.execute('SELECT content FROM documents WHERE id != %(id)s ORDER BY embedding <=> (SELECT embedding FROM documents WHERE id = %(id)s) LIMIT 5', {'id': document_id}).fetchall()
    for neighbor in neighbors:
        print(neighbor[0])

    print("neighbors", neighbors)
    return neighbors

