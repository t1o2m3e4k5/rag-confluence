from pydantic import BaseModel, Field

class IndexResponse(BaseModel):
    processed_pages: int = Field(..., description="Ile stron zaktualizowano/wstawiono")

class ChatRequest(BaseModel):
    prompt: str
    thread_id: str = Field(..., description="Identyfikator wątku rozmowy")

class ChatResponse(BaseModel):
    answer: str