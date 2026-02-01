import asyncio
import grpc.experimental.aio as grpc_aio

grpc_aio.init_grpc_aio()

from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    context_precision,
    answer_relevancy,
)

from prod_assistant.utils.model_loader import ModelLoader


model_loader = ModelLoader()


# -------------------------------------------------------------------
# Context Precision (NO reference answer)
# -------------------------------------------------------------------
def evaluate_context_precision(query: str, response: str, retrieved_contexts: list[str]):
    sample = SingleTurnSample(
        user_input=query,
        response=response,
        retrieved_contexts=retrieved_contexts,
    )

    async def _run():
        llm = model_loader.load_llm()
        evaluator_llm = LangchainLLMWrapper(llm)

        metric = context_precision(llm=evaluator_llm)
        return await metric.single_turn_ascore(sample)

    return asyncio.run(_run())


# -------------------------------------------------------------------
# Response Relevancy (LLM + embeddings)
# -------------------------------------------------------------------
def evaluate_response_relevancy(query: str, response: str, retrieved_contexts: list[str]):
    sample = SingleTurnSample(
        user_input=query,
        response=response,
        retrieved_contexts=retrieved_contexts,
    )

    async def _run():
        llm = model_loader.load_llm()
        evaluator_llm = LangchainLLMWrapper(llm)

        # ✅ RAW LangChain embeddings (NO adapter, NO wrapper)
        embeddings = model_loader.load_embeddings()

        metric = answer_relevancy(
            llm=evaluator_llm,
            embeddings=embeddings,
        )

        return await metric.single_turn_ascore(sample)

    return asyncio.run(_run())
