import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

CONN = "postgresql+psycopg://postgres:authentication@localhost:15457/postgres"


vector_store = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name="confluence_docs",
    connection=CONN,
    use_jsonb=True,
)


query = "What is project Alpha about?"
docs = vector_store.similarity_search(query, k=2)
for d in docs:
    print(d.page_content[:120], d.metadata)