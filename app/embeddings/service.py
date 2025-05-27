from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from app.config import get_settings

_settings = get_settings()

class EmbeddingService:
    def __init__(self):
        if _settings.embed_model_name.startswith("sentence-transformers"):
            self._model = HuggingFaceEmbeddings(model_name=_settings.embed_model_name)
        else:
            self._model = OpenAIEmbeddings(model=_settings.embed_model_name)

    @property
    def model(self):
        return self._model