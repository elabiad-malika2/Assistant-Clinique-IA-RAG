import mlflow
import os

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
mlflow.set_experiment("CliniQ_RAG_Production")

def log_to_mlflow(question: str, response: str, contexts: list, metrics: dict):
    
    print("Sauvegarde dans MLflow...")
    
    with mlflow.start_run():

        mlflow.log_params({
            # Chunking
            "chunking_strategy": "MarkdownHeader + custom_table_preservation",
            "max_chunk_size": 1200,
            "min_chunk_size": 200,
            
            # Embedding
            "embedding_model": "dangvantuan/sentence-camembert-base",
            "embedding_dimension": 768,
            
            # Vector DB
            "vector_db": "ChromaDB",
            "index_type": "HNSW",
            "distance_metric": "cosine",
            
            # Retrieval
            "retrieval_top_k": 5,
            
            # Reranking
            "reranker_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "reranker_top_n": 3,
        })

        
        mlflow.log_params({
            "llm_provider": "Google Generative AI",
            "llm_model": "gemini-flash-latest",
            "temperature": 0.1,
            "prompt_type": "CliniQ_Strict_Medical_Prompt",
        })

        
        mlflow.log_text(question, "artifacts/question.txt")
        mlflow.log_text(response, "artifacts/response.txt")
        mlflow.log_text("\n\n---\n\n".join(contexts), "artifacts/contexts.txt")

        
        if metrics:
            mlflow.log_metrics(metrics)

    print("Données visibles sur http://localhost:5000 !")