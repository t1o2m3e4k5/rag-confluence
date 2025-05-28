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
├── demo/             # Demo and example scripts
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

- Python 3.12
- Docker and Docker Compose
- PostgreSQL with pgvector extension

## Setup Instructions

1. Create and activate virtual environment (python 3.12.3 was used):
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux Ubuntu
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```powershell
# Windows PowerShell
.\.venv\Scripts\pip.exe install -r .\requirements.txt

# Linux Ubuntu
pip install -r requirements.txt
```

3. Configure environment:
```powershell
cp .env.example .env  # Update with your credentials

```

4. Start PostgreSQL with pgvector:
```powershell
docker compose up -d
```

5. Initialize vector extension in PostgreSQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

6. Run the application:
```powershell
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# in the background - logs will be saved to `app.log` in the current directory.
nohup uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &
```




7. stop the application:
```
# Linux Ubuntu
ps aux | grep "uvicorn app.api.main:app" | grep -v grep
kill {process ID}
```


8. update vector store for specific Confluence space (e.g. TS)
```
curl --location 'http://ec2-35-164-165-32.us-west-2.compute.amazonaws.com:8000/index/TS' \
--header 'Content-Type: application/json' \
--data '{"frontend_token": "secret_token"}'
```


## Development

- The application uses FastAPI for the REST API
- LangChain and LangGraph for RAG implementation
- PostgreSQL with pgvector for vector storage


## AWS EC2 instance ssh connection
ssh -i "AWS_personal_2keypair.pem" ubuntu@ec2-35-164-165-32.us-west-2.compute.amazonaws.com


## HTTP access to the app
http://ec2-35-164-165-32.us-west-2.compute.amazonaws.com:8000/


## HTTP access to the Confluence
http://ec2-35-164-165-32.us-west-2.compute.amazonaws.com:8090/

# Install a Confluence Data Center trial
https://confluence.atlassian.com/doc/install-a-confluence-data-center-trial-838416249.html

# Github repo 
https://github.com/t1o2m3e4k5/rag-confluence


