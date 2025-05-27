# app/config.py
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from dotenv import load_dotenv


# Kompatybilnie z obiema gałęziami Pydantic:
try:
    # Pydantic v2 – oficjalny sposób
    from pydantic_settings import BaseSettings
except ImportError:  # fallback dla Pydantic v1
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # DB
    pg_dsn: str = Field(..., env="PG_DSN")  # postgresql+psycopg2://user:pwd@host/db

    # Confluence
    confluence_url: str = Field(..., env="CONFLUENCE_URL")
    confluence_token: str = Field(..., env="CONFLUENCE_TOKEN")
    frontend_token: str = Field(..., env="FRONTEND_TOKEN")

    # Embeddings / LLM
    embed_model_name: str = "sentence-transformers/all-mpnet-base-v2"
    llm_model_name: str = "gpt-4o-mini"
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")

    class Config:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        print("------------------------------------ env_path {}".format(env_path))
        load_dotenv(dotenv_path=env_path)        

@lru_cache
def get_settings() -> Settings:
    return Settings()