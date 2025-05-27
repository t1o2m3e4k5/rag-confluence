# Design and Implementation of an Application Leveraging Retrieval-Augmented Generation and Large Language Models for Searching and Presenting Information from a Confluence Knowledge Base

## Academic Context
This project is a postgraduate thesis in Artificial Intelligence – Machine Learning studies at WSB Merito University in Gdańsk.


## Project Overview
This project implements a Retrieval-Augmented Generation (RAG) system that enhances information retrieval from Confluence knowledge bases using Large Language Models (LLMs).

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
app/
├── __init__.py
├── config.py          # Central configuration and secrets management
├── confluence/
│   ├── __init__.py
│   ├── client.py      # Thin wrapper over atlassian-python-api
│   └── loader.py      # Page loading and metadata enrichment
├── embeddings/
│   ├── __init__.py
│   └── service.py     # Abstraction over embedding models
├── vectorstore/
│   ├── __init__.py
│   └── repository.py  # CRUD operations and upsert in PGVector
├── rag/
│   ├── __init__.py
│   ├── agent.py       # LangGraph agent creation
│   └── retrieval.py   # LangChain Tools implementation
├── api/
│   ├── __init__.py
│   ├── schemas.py     # Pydantic request/response models
│   └── main.py        # FastAPI endpoints
```

## Layer Dependencies

```
config  →  confluence.client
              ↑
embeddings    |
      ↑       |
vectorstore.repository ← rag.retrieval ← rag.agent
                                ↑
                               api.main
```

## Prerequisites

- Python 3.11
- Docker and Docker Compose
- PostgreSQL with pgvector extension

## Setup Instructions

1. Create and activate virtual environment (python 3.11 was used):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
.\.venv\Scripts\pip.exe install -r .\requirements.txt
```

3. Configure environment:
```powershell
cp .env.example .env  # Update with your credentials
```

4. Start PostgreSQL with pgvector:
```powershell
docker-compose up -d
```

5. Initialize vector extension in PostgreSQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

6. Run the application:
```powershell
uvicorn app.api.main:app --reload
```

## Development

- The application uses FastAPI for the REST API
- LangChain and LangGraph for RAG implementation
- PostgreSQL with pgvector for vector storage