# app/vectorstore/repository.py
from typing import Sequence
from langchain_postgres import PGVector
from langchain_core.documents import Document
from app.config import get_settings
from app.embeddings.service import EmbeddingService
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

_settings = get_settings()

class VectorStoreRepository:


    def __init__(self, collection_name: str = "confluence_docs"):
        self.store = PGVector(
            embeddings=EmbeddingService().model,
            collection_name=collection_name,
            connection=_settings.pg_dsn,
        )
        

    # ---------- public API ----------

    def insert_documents(self, docs: Sequence[Document]):
        """Wstawia dokumenty *bez* upsertu; zakładamy, że stare zostały skasowane."""
        self.store.create_collection() #Collection not found error if defeted manually
        self.store.add_documents(documents=docs)  # uuid4 generowane automatycznie


    def delete_by_space(self, space_key: str):
        """Deletes documents from the vector store where cmetadata->>'space_key' matches the given space_key."""
        
        # self.store.delete(filter={"space_key": space_key}) does not work :(
        
        # Create a SQLAlchemy engine from the connection string
        engine = create_engine(_settings.pg_dsn)
        
        # Execute the delete query with JSONB filter
        with Session(engine) as session:
            session.execute(
                text("DELETE FROM langchain_pg_embedding WHERE cmetadata->>'space_key' = :space_key"),
                {"space_key": space_key}
            )
            session.commit()

    def similarity_search(self, query: str, k: int = 2):
        return self.store.similarity_search(query, k=k)
    