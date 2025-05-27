import datetime as dt
from langchain_community.document_loaders import ConfluenceLoader
from langchain_core.documents import Document
from .client import ConfluenceClient
from app.config import get_settings

_settings = get_settings()

class ConfluencePageLoader:
    """Ładuje strony oraz wzbogaca metadata."""

    def __init__(self, client: ConfluenceClient | None = None):
        self.client = client or ConfluenceClient()
        self.base_loader = ConfluenceLoader(
            url=_settings.confluence_url,
            token=_settings.confluence_token,
        )

    def load_space(self, space_key: str, page_limit: int = 200) -> list[Document]:

        self.base_loader.space_key = space_key
        self.base_loader.limit = page_limit
        raw_docs = self.base_loader.load()

        # raw_docs = self.base_loader.load(space_key=space_key, limit=page_limit)
        for doc in raw_docs:
            page_id = doc.metadata["id"]
            full = self.client.fetch_page(page_id)

            doc.metadata.update(
                {
                    "author": full.get("history", {})
                    .get("createdBy", {})
                    .get("displayName", "Unknown"),
                    "last_modified": self._iso(full.get("version", {}).get("when")),
                    "space_key": space_key,
                }
            )
        return raw_docs

    @staticmethod
    def _iso(when: str | None) -> str | None:
        if not when:
            return None
        return dt.datetime.fromisoformat(when.replace("Z", "+00:00")).isoformat()