import os
from typing import List
from dotenv import load_dotenv

from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever

from prod_assistant.utils.config_loader import load_config
from prod_assistant.utils.model_loader import ModelLoader
from prod_assistant.evaluation.ragas_eval import (
    evaluate_context_precision,
    evaluate_response_relevancy,
)


class Retriever:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.config = load_config()
        self._load_env_variables()

        
        self.vstore = None
        self.retriever_instance = None

    def _load_env_variables(self):
        load_dotenv()

        required_vars = [
            "GOOGLE_API_KEY",
            "ASTRA_DB_API_ENDPOINT",
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_KEYSPACE",
        ]

        missing_vars = [v for v in required_vars if not os.getenv(v)]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")

        self.google_api_key = os.getenv("GOOGLE_API_KEY").strip()
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT").strip()
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN").strip()
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE").strip()

    def load_retriever(self) -> ContextualCompressionRetriever:
        """Lazy-load and cache the retriever"""

        # -------------------------------
        # Vector store (loaded once)
        # -------------------------------
        if self.vstore is None:
            collection_name = self.config["astra_db"]["collection_name"]

            self.vstore = AstraDBVectorStore(
                embedding=self.model_loader.load_embeddings(),
                collection_name=collection_name,
                api_endpoint=self.db_api_endpoint,
                token=self.db_application_token,
                namespace=self.db_keyspace,
            )

        # -------------------------------
        # Retriever (loaded once)
        # -------------------------------
        if self.retriever_instance is None:
            top_k = self.config.get("retriever", {}).get("top_k", 3)

            base_retriever = self.vstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": top_k,
                    "fetch_k": 20,
                    "lambda_mult": 0.7,
                    "score_threshold": 0.6,
                },
            )

            llm = self.model_loader.load_llm()
            compressor = LLMChainFilter.from_llm(llm)

            self.retriever_instance = ContextualCompressionRetriever(
                base_retriever=base_retriever,
                base_compressor=compressor,
            )

            print("Retriever loaded successfully.")

        return self.retriever_instance

    def call_retriever(self, user_query: str) -> List[Document]:
        retriever = self.load_retriever()
        return retriever.invoke(user_query)


# ---------------------------------------------------------
# Local test
# ---------------------------------------------------------
if __name__ == "__main__":
    retriever_obj = Retriever()
    user_query = "How is the performance of the iPhone 15?"
    results = retriever_obj.call_retriever(user_query)

    for idx, doc in enumerate(results):
        print(f"\nResult {idx}")
        print(doc.page_content)
        print("Metadata:", doc.metadata)
