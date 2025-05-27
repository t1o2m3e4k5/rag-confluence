# Projekt i implementacja aplikacji wykorzystującej Retrieval-Augmented Generation oraz duże modele językowe do wyszukiwania i prezentacji informacji z bazy wiedzy Confluence

## Kontekst Akademicki
Ten projekt jest pracą dyplomową na studiach podyplomowych Artificial Intelligence – Machine Learning na Uniwersytecie WSB Merito w Gdańsku.

## Przegląd Projektu
Ten projekt implementuje system Retrieval-Augmented Generation (RAG), który usprawnia wyszukiwanie informacji z baz wiedzy Confluence przy wykorzystaniu dużych modeli językowych (LLM).

## Architektura

Aplikacja opiera się na modułowej architekturze z jasnym podziałem odpowiedzialności:

```
app/
├── __init__.py
├── config.py          # Centralna konfiguracja i zarządzanie sekretami
├── confluence/
│   ├── __init__.py
│   ├── client.py      # Cienka nakładka na atlassian-python-api
│   └── loader.py      # Ładowanie stron i wzbogacanie metadanych
├── embeddings/
│   ├── __init__.py
│   └── service.py     # Abstrakcja nad modelami embedującymi
├── vectorstore/
│   ├── __init__.py
│   └── repository.py  # Operacje CRUD i upsert w PGVector
├── rag/
│   ├── __init__.py
│   ├── agent.py       # Tworzenie agenta LangGraph
│   └── retrieval.py   # Implementacja narzędzi LangChain
├── api/
│   ├── __init__.py
│   ├── schemas.py     # Modele Pydantic dla request/response
│   └── main.py        # Endpointy FastAPI
```

## Zależności między Warstwami

```
config  →  confluence.client
              ↑
embeddings    |
      ↑       |
vectorstore.repository ← rag.retrieval ← rag.agent
                                ↑
                               api.main
```

## Wymagania

- Python 3.11
- Docker i Docker Compose
- PostgreSQL z rozszerzeniem pgvector

## Instrukcja Instalacji

1. Utwórz i aktywuj środowisko wirtualne:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Zainstaluj zależności:
```powershell
.\.venv\Scripts\pip.exe install -r .\requirements.txt
```

3. Skonfiguruj środowisko:
```powershell
cp .env.example .env  # Zaktualizuj swoimi danymi
```

4. Uruchom PostgreSQL z pgvector:
```powershell
docker-compose up -d
```

5. Zainicjalizuj rozszerzenie vector w PostgreSQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

6. Uruchom aplikację:
```powershell
uvicorn app.api.main:app --reload
```

## Rozwój

- Aplikacja wykorzystuje FastAPI dla API REST
- LangChain i LangGraph do implementacji RAG
- PostgreSQL z pgvector do przechowywania wektorów