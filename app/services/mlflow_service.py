# app/services/mlflow_service.py

import mlflow
import os

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
mlflow.set_experiment("CliniQ_RAG_Production")

def log_to_mlflow(question: str, response: str, contexts: list, metrics: dict):
    """
    Enregistre absolument TOUT dans le tableau de bord MLflow.
    """
    print("📝 Sauvegarde dans MLflow...")
    
    with mlflow.start_run():
        
        # 1. Logger les paramètres du RAG
        mlflow.log_params({
            "chunk_size": 1200,
            "chunk_overlap": 100,
            "chunk_strategy": "MarkdownHeaderTextSplitter",
            "embedding_model": "dangvantuan/sentence-camembert-base",
            "embedding_dim": 768,
            "retrieval_algo": "cosine",
            "retrieval_k": 5,
            "reranking_model": "ms-marco-MiniLM-L-6-v2"
        })
        
        # 2. Logger les paramètres du LLM (Gemini)
        mlflow.log_params({
            "llm_model": "gemini-flash-latest",
            "temperature": 0.1,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 1024,
            "prompt_template": "CliniQ_Strict_Medical_Prompt"
        })
        
        # 3. Logger les réponses et contextes (dans des petits fichiers textes lisibles sur l'interface)
        mlflow.log_text(question, "logs/question.txt")
        mlflow.log_text(response, "logs/response.txt")
        mlflow.log_text("\n\n---\n\n".join(contexts), "logs/contexts.txt")
        
        # 4. Logger les 4 notes données par DeepEval
        mlflow.log_metrics(metrics)
        
    print(" Données visibles sur http://localhost:5000 !")