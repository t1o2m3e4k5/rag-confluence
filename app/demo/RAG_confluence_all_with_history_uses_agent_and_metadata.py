import os
import datetime as dt
from typing_extensions import List, TypedDict

from atlassian import Confluence

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain_postgres import PGVector
from langchain_community.document_loaders import ConfluenceLoader
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, StateGraph



# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGSMITH_API_KEY"] = "*****************************************"
# os.environ["LANGSMITH_PROJECT"] = "***********"



# ---------------------------------------------------------------------------
# 1. LLM & embeddings
# ---------------------------------------------------------------------------
llm = init_chat_model("gpt-4o-mini", model_provider="openai")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# ---------------------------------------------------------------------------
# 2. Vector store (metadata is stored as JSONB automatically by PGVector)
# ---------------------------------------------------------------------------
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="confluence_docs",
    connection="postgresql+psycopg2://postgres:authentication@localhost:15457/postgres",
)

# ---------------------------------------------------------------------------
# 3. Load pages from Confluence, then enrich with extra metadata
# ---------------------------------------------------------------------------
CONFLUENCE_URL = "http://localhost:8090"

CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")
SPACE_KEY = "TS"
PAGE_LIMIT = 50

# (a) Primary loader – gets page content and basic metadata
loader = ConfluenceLoader(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
raw_docs = loader.load(space_key=SPACE_KEY, include_attachments=False, limit=PAGE_LIMIT)
print(f"Loaded {len(raw_docs)} Confluence pages from space '{SPACE_KEY}'.")

# (b) Secondary call via Atlassian SDK to fetch richer metadata for each page
confluence_api = Confluence(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)

ENRICH_KEYS = ("id", "author", "last_modified")

for doc in raw_docs:
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

# ---------------------------------------------------------------------------
# 4. Split into chunks (rich metadata travels with each chunk)
# ---------------------------------------------------------------------------
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(raw_docs)
print(f"Split pages into {len(all_splits)} sub‑documents.")

# ---------------------------------------------------------------------------
# 5. Persist to PGVector
# ---------------------------------------------------------------------------
_ = vector_store.add_documents(documents=all_splits)
print("Chunks (with metadata) stored in PGVector.")

# ---------------------------------------------------------------------------
# 6. Retrieval tool – surfaces new metadata to the agent
# ---------------------------------------------------------------------------
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve the 2 most similar chunks."""
    retrieved_docs = vector_store.similarity_search(query, k=2)

    serialised = "\n\n".join(
        (
            f"Source: {doc.metadata.get('source', doc.metadata.get('url', 'N/A'))}\n"
            f"Author: {doc.metadata.get('author', 'Unknown')}\n"
            f"Last modified: {doc.metadata.get('last_modified', 'Unknown')}\n"
            f"Content: {doc.page_content}"
        )
        for doc in retrieved_docs
    )
    return serialised, retrieved_docs

# ---------------------------------------------------------------------------
# 7. Agent wiring
# ---------------------------------------------------------------------------

memory = MemorySaver()
agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)

CONFIG = {"configurable": {"thread_id": "def23421"}}

if __name__ == "__main__":
    # Simple smoke‑test – the agent will use the new metadata in its answers
    questions = [
        "Hello, my name is Tomek",
        "What is my name?",
        (
            "What are the components of Project Alpha service?\n\n"
            "Once you get the answer, describe releases of this project. Add info about the author of a confluence page"
        ),
    ]

    for q in questions:
        print("\nUSER:", q)
        for event in agent_executor.stream(
            {"messages": [{"role": "user", "content": q}]},
            stream_mode="values",
            config=CONFIG,
        ):
            event["messages"][-1].pretty_print()