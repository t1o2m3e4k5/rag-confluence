# Projekt i Implementacja Aplikacji Wykorzystującej Retrieval-Augmented Generation i Modele Językowe do Wyszukiwania i Prezentacji Informacji z Bazy Wiedzy Confluence

## Kontekst Akademicki
Ten projekt jest pracą dyplomową na studiach podyplomowych Artificial Intelligence – Machine Learning na Uniwersytecie WSB Merito w Gdańsku.

## Przegląd Projektu
Ten projekt implementuje system Retrieval-Augmented Generation (RAG), który ulepsza wyszukiwanie informacji z baz wiedzy Confluence przy użyciu dużych modeli językowych (LLM).

## Architektura

Aplikacja opiera się na architekturze modułowej z jasnym podziałem odpowiedzialności:

```
app/
├── __init__.py
├── config.py          # Centralna konfiguracja i zarządzanie sekretami
├── confluence/
│   ├── __init__.py
│   ├── client.py      # Cienka warstwa opakowująca atlassian-python-api
│   └── loader.py      # Ładowanie stron i wzbogacanie metadanych
├── embeddings/
│   ├── __init__.py
│   └── service.py     # Abstrakcja nad modelami embeddingowymi
├── vectorstore/
│   ├── __init__.py
│   └── repository.py  # Operacje CRUD i upsert w PGVector
├── rag/
│   ├── __init__.py
│   ├── agent.py       # Tworzenie agenta LangGraph
│   └── retrieval.py   # Implementacja narzędzi LangChain
├── api/
│   ├── __init__.py
│   ├── schemas.py     # Modele Pydantic dla żądań/odpowiedzi
│   └── main.py        # Endpointy FastAPI
├── demo/             # Skrypty demonstracyjne i przykłady
```

## Zależności Warstw

```
config  →  confluence.client
              ↑
embeddings    |
      ↑       |
vectorstore.repository ← rag.retrieval ← rag.agent
                                ↑
                               api.main
```

## Wymagania Wstępne

- Python 3.12
- Docker i Docker Compose
- PostgreSQL z rozszerzeniem pgvector

## Instrukcje Instalacji

1. Utwórz i aktywuj środowisko wirtualne (użyto Pythona 3.12.3):
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux Ubuntu
python -m venv .venv
source .venv/bin/activate
```

2. Zainstaluj zależności:
```powershell
# Windows PowerShell
.\.venv\Scripts\pip.exe install -r .\requirements.txt

# Linux Ubuntu
pip install -r requirements.txt
```

3. Skonfiguruj środowisko:
```powershell
cp .env.example .env  # Zaktualizuj swoimi danymi uwierzytelniającymi
```

4. Uruchom PostgreSQL z pgvector:
```powershell
docker compose up -d
```

5. Zainicjalizuj rozszerzenie wektorowe w PostgreSQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

6. Uruchom aplikację:
```powershell
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# w tle - logi będą zapisywane do `app.log` w bieżącym katalogu
nohup uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &
```

7. Zatrzymaj aplikację:
```
# Linux Ubuntu
ps aux | grep "uvicorn app.api.main:app" | grep -v grep
kill {ID procesu}
```

8. Zaktualizuj magazyn wektorowy dla konkretnej przestrzeni Confluence (np. TS):
```
curl --location 'http://ec2-35-164-165-32.us-west-2.compute.amazonaws.com:8000/index/TS' \
--header 'Content-Type: application/json' \
--data '{"frontend_token": "secret_token"}'
```

## Rozwój

- Aplikacja używa FastAPI dla API REST
- LangChain i LangGraph do implementacji RAG
- PostgreSQL z pgvector do przechowywania wektorów

## Połączenie SSH z instancją AWS EC2
ssh -i "AWS_personal_2keypair.pem" ubuntu@ec2-35-164-165-32.us-west-2.compute.amazonaws.com

## Dostęp HTTP do aplikacji
http://ec2-35-164-165-32.us-west-2.compute.amazonaws.com:8000/

## Dostęp HTTP do Confluence
http://ec2-35-164-165-32.us-west-2.compute.amazonaws.com:8090/

# Instalacja wersji próbnej Confluence Data Center
https://confluence.atlassian.com/doc/install-a-confluence-data-center-trial-838416249.html 