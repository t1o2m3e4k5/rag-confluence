from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.confluence.loader import ConfluencePageLoader
from app.vectorstore.repository import VectorStoreRepository
from app.rag.agent import stream_answer
from app.embeddings.service import EmbeddingService
from app.config import get_settings
from .schemas import IndexResponse, ChatRequest, ChatResponse
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_core.messages.ai import AIMessage

app = FastAPI(title="Confluence RAG API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

_settings = get_settings()
_repo = VectorStoreRepository()
_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # nadaje metadata: {"chunk": i}

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/index/{space_key}", response_model=IndexResponse)
async def index_space(space_key: str):
    """(Re)build the vector index for a given Confluence space.

    - **Prosta strategia**: najpierw *usuń* wszystkie istniejące wektory danego `space_key`,
      potem dodaj świeżo wygenerowane.  Zero logiki inkrementalnej.
    """
    loader = ConfluencePageLoader()
    raw_docs = loader.load_space(space_key)
    splits = _splitter.split_documents(raw_docs)

    # 1️⃣ wyczyść stare chunk‑i
    _repo.delete_by_space(space_key)

    # 2️⃣ zapisz nowe
    _repo.insert_documents(splits)

    return IndexResponse(processed_pages=len(splits))

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Validate frontend token
    if not req.frontend_token or req.frontend_token != _settings.frontend_token:
        raise HTTPException(status_code=403, detail="Invalid frontend token")
        
    chunks = []
    for part in stream_answer(req.prompt, req.thread_id):
        if isinstance(part, AIMessage):
            chunks.append(part.content)
    return ChatResponse(answer="".join(chunks))
