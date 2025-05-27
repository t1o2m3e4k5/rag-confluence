from atlassian import Confluence
#from .models import PageMeta  # dataclass
from app.config import get_settings

_settings = get_settings()

class ConfluenceClient:
    """Cienka nakładka ułatwiająca mockowanie w testach."""

    def __init__(self):
        self._api = Confluence(
            url=_settings.confluence_url,
            token=_settings.confluence_token,
        )

    def fetch_page(self, page_id: str) -> dict:  # raw JSON
        return self._api.get_page_by_id(page_id, expand="version,history")

    def fetch_space_pages(self, space_key: str, limit: int = 100) -> list[dict]:
        # Można dodać obsługę stronicowania
        return self._api.get_all_pages_from_space(space_key, start=0, limit=limit)