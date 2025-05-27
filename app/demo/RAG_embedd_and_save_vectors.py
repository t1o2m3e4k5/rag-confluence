import getpass
import os
import datetime as dt
from langchain_huggingface import HuggingFaceEmbeddings
from atlassian import Confluence  # lightweight REST wrapper

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

from langchain_postgres import PGVector

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="confluence_docs",
    connection="postgresql+psycopg2://postgres:authentication@localhost:15457/postgres"
)



import bs4
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import ConfluenceLoader

CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")
CONFLUENCE_URL = "http://localhost:8090"
SPACE_KEY = "TS"
PAGE_LIMIT = 50

loader = ConfluenceLoader(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
docs = loader.load(
    space_key=SPACE_KEY, include_attachments=False, limit=PAGE_LIMIT #include_attachments=True
)

print(f"Number of docs: {len(docs)}.")


# Secondary call via Atlassian SDK to fetch richer metadata for each page
confluence_api = Confluence(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)

ENRICH_KEYS = ("id", "author", "last_modified")

for doc in docs:
    page_id = doc.metadata.get("id")
    if page_id is None:
        continue  # safety – shouldn't happen

    api_page = confluence_api.get_page_by_id(page_id, expand="version,history")

    # Author (who created the page)
    author = (
        api_page.get("history", {})
        .get("createdBy", {})
        .get("displayName", "Unknown")
    )

    last_modified_raw = api_page.get("version", {}).get("when", None)
    try:
        last_modified = dt.datetime.fromisoformat(last_modified_raw.replace("Z", "+00:00"))
    except Exception:
        last_modified = None

    # Attach to metadata so the information survives the text splitter
    doc.metadata.update({
        "author": author,
        "last_modified": last_modified.isoformat() if last_modified else None,
    })



text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

print(f"Split blog post into {len(all_splits)} sub-documents.")

_ = vector_store.add_documents(documents=all_splits)

