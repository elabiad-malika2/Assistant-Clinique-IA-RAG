import os
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from mlops.local_llm import LocalModel
from deepeval.test_case import LLMTestCase
from deepeval.models import GeminiModel
from google.genai.errors import ServerError 
from deepeval.models import OllamaModel


def _build_ollama_model():
    """
    Modèle d'évaluation local via Ollama.
    Change 'phi3' par le modèle que tu veux si besoin.
    """
    return OllamaModel(
        model="phi3",                 # ou "mistral", "llama3", etc.
        base_url="http://host.docker.internal:11434",  # important pour Docker
        temperature=0.0,
    )


def evaluate_rag_response(question: str, response: str, contexts: list) -> dict:
    print(" Calcul des 4 notes DeepEval avec Gemini en cours...")

    test_case = LLMTestCase(
        input=question,
        actual_output=response,
        retrieval_context=contexts,
        expected_output=response,
    )

    
    model = _build_ollama_model()

    relevancy = AnswerRelevancyMetric(threshold=0.7, model=model)
    faithfulness = FaithfulnessMetric(threshold=0.7, model=model)
    precision = ContextualPrecisionMetric(threshold=0.7, model=model)
    recall = ContextualRecallMetric(threshold=0.7, model=model)

    relevancy.measure(test_case)
    faithfulness.measure(test_case)
    precision.measure(test_case)
    recall.measure(test_case)

    print(" Notation DeepEval terminée !")

    return {
            "answer_relevance": relevancy.score,
            "faithfulness": faithfulness.score,
            "precision_at_k": precision.score,
            "recall_at_k": recall.score,
        }    
