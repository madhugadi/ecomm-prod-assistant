import os
import sys
from dotenv import load_dotenv

from prod_assistant.utils.config_loader import load_config
from prod_assistant.logger import GLOBAL_LOGGER as log
from prod_assistant.exception.custom_exception import ProductAssistantException

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


class ApiKeyManager:
    """
    Centralized API key loader.
    Ensures .env always overrides OS / IDE cached values.
    """

    def __init__(self):
        load_dotenv(override=True)

        self.api_keys = {
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "ASTRA_DB_API_ENDPOINT": os.getenv("ASTRA_DB_API_ENDPOINT"),
            "ASTRA_DB_APPLICATION_TOKEN": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            "ASTRA_DB_KEYSPACE": os.getenv("ASTRA_DB_KEYSPACE"),
        }

        endpoint = self.api_keys.get("ASTRA_DB_API_ENDPOINT")
        if endpoint and endpoint.lower().startswith("set "):
            raise RuntimeError(
                "ASTRA_DB_API_ENDPOINT polluted with Windows 'set' syntax"
            )

        for key, val in self.api_keys.items():
            if val:
                log.info(f"{key} loaded from environment")
            else:
                log.warning(f"{key} is missing from environment")

    def get(self, key: str):
        return self.api_keys.get(key)


class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    GROQ ONLY.
    """

    def __init__(self):
        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    def load_embeddings(self):
        try:
            model_name = (
                self.config
                .get("embedding_model", {})
                .get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
            )

            log.info("Loading HuggingFace embeddings", model=model_name)

            return HuggingFaceEmbeddings(model_name=model_name)

        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise ProductAssistantException(
                "Failed to load embedding model",
                sys,
            )

    # ------------------------------------------------------------------
    # LLM (GROQ ONLY)
    # ------------------------------------------------------------------
    def load_llm(self):
        llm_block = self.config.get("llm", {})

        # Default to GROQ
        provider_key = os.getenv("LLM_PROVIDER", "groq")

        if provider_key not in llm_block:
            raise ValueError(f"LLM provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)

        log.info("Loading LLM", provider="groq", model=model_name)

        groq_key = self.api_key_mgr.get("GROQ_API_KEY")
        if not groq_key:
            raise EnvironmentError("GROQ_API_KEY is not set")

        return ChatGroq(
            model=model_name,
            api_key=groq_key,
            temperature=temperature,
        )
