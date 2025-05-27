# app/config.py
from functools import lru_cache
from pathlib import Path
#from pydantic import BaseSettings, Field
from pydantic import Field
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

    # Embeddings / LLM
    embed_model_name: str = "sentence-transformers/all-mpnet-base-v2"
    llm_model_name: str = "gpt-4o-mini"
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        print("------------------------------------ env_file {}".format(env_file))
        #env_file = Path(__file__).with_name(".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()