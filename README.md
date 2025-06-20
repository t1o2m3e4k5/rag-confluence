# Design and Implementation of an Application Leveraging RAG and LLMs for Searching and Presenting Information from a Confluence Knowledge Base

## Academic Context
This project is a postgraduate thesis in Artificial Intelligence – Machine Learning studies at WSB Merito University in Gdańsk.


## Project Overview
This project implements a Retrieval-Augmented Generation (RAG) system that enhances information retrieval from Confluence knowledge base using Large Language Models (LLMs).

## Key Features

### Agentic RAG Approach
The application uses an agentic RAG approach. This mechanism enables iterative communication with the embedding model – for example, it runs the vector search, evaluates the relevance of results, and if information is missing, it automatically generates a new search query and repeats the step.

### Conversation Memory
Additionally, the application remembers the conversation history with the user (according to the `thread_id` parameter).

### Hybrid Vector Search
Another feature is the hybrid approach to vector search, which allows filtering results using metadata. Currently, in the vector database, the following metadata is stored in a JSONB type column: `id`, `when`, `title`, `author`, `source`, `space_key`, `last_modified`. Adding additional fields is straightforward.

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


## API Endpoints

The application provides the following endpoints:

### 1. POST /index/{spaceKey}
Reindexes the selected Confluence space. Results are saved in the PostgreSQL database.

**Example:**
```bash
curl --location 'http://localhost:8000/index/TS' \
--header 'Content-Type: application/json' \
--data '{"frontend_token": "secret_token"}'
```

### 2. POST /chat
Returns a response from the LLM. 

**Parameters:**
- `prompt` - contains the user query
- `thread_id` - contains a string that serves as the conversation identifier (conversation history is remembered within this parameter)
- `frontend_token` - protection against unauthorized use of the model. This value is set in the `.env` file

**Example:**
```bash
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "What is the latest update on project X?",
    "thread_id": "thread-ABCDE",
    "frontend_token": "secret_token"
}'
```

### 3. Web Interface
Additionally, the application exposes a web page with a user interface, allowing users to conduct conversations directly from the browser.

## Development

- The application uses FastAPI for the REST API
- LangChain and LangGraph for RAG implementation
- PostgreSQL with pgvector for vector storage

## Future Improvements

The following enhancements are planned for future development:

### Improved Reindexing Mechanism
Enhance the reindexing mechanism for selected Confluence spaces (`POST /index/{spaceKey}`). Currently, all vectors for a given Confluence space are deleted and recreated, which is a very time-consuming process for large knowledge bases. This mechanism should update/add/delete only changed Confluence pages (based on Change Data Capture principles).

### Attachment Indexing
Add indexing support for attachments. Currently, only text data is indexed, but the system could be extended to process and index document attachments such as PDFs, Word documents, and other file types.

### Conversation History Management
Implement limits on the size of stored conversation history.

### Role-Based Access Control (RBAC)
Implement Role-Based Access Control to provide fine-grained permissions and security, allowing different user roles to access different Confluence spaces and features based on their authorization level.

# Install a Confluence Data Center trial
https://confluence.atlassian.com/doc/install-a-confluence-data-center-trial-838416249.html

# Github repo 
https://github.com/t1o2m3e4k5/rag-confluence


