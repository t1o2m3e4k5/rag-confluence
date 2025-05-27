from pydantic import BaseModel, Field

class IndexRequest(BaseModel):
    frontend_token: str = Field(..., description="Token required for authentication")

class IndexResponse(BaseModel):
    processed_pages: int = Field(..., description="Ile stron zaktualizowano/wstawiono")

class ChatRequest(BaseModel):
    prompt: str
    thread_id: str = Field(..., description="Identyfikator wątku rozmowy")
    frontend_token: str = Field(..., description="Token for frontend validation")

class ChatResponse(BaseModel):
    answer: str