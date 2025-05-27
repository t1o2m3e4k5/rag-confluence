from langchain_core.tools import tool
from app.vectorstore.repository import VectorStoreRepository

_repo = VectorStoreRepository()

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """LangChain Tool – zwraca 2 najtrafniejsze kawałki."""
    docs = _repo.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {d.metadata.get('url', 'N/A')}\n"  # + inne pola
        f"Author: {d.metadata.get('author', 'Unknown')}\n"
        f"Last modified: {d.metadata.get('last_modified', 'Unknown')}\n"
        f"Content: {d.page_content}"
        for d in docs
    )
    return serialized, docs