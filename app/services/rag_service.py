# app/services/rag_service.py

from sqlalchemy.orm import Session
from app.models.query import Query
from rag.rag_pipeline import ask_clinical_assistant
from mlops.deepeval_metrics import evaluate_rag_response
from app.services.mlflow_service import log_to_mlflow

from monitoring.prometheus_metrics import (
    RAG_REQUESTS_TOTAL, 
    RAG_ERRORS_TOTAL, 
    RAG_ANSWER_RELEVANCE, 
    RAG_FAITHFULNESS
)

def process_and_save_query(db: Session, user_id: int, question: str):
    
    RAG_REQUESTS_TOTAL.inc()
    
    try:
        reponse_ia, sources = ask_clinical_assistant(question)
        
        nouvelle_requete = Query(query=question, reponse=reponse_ia, user_id=user_id)
        db.add(nouvelle_requete)
        db.commit()
        db.refresh(nouvelle_requete)
        
    except Exception as e:
        RAG_ERRORS_TOTAL.inc()
        print(f" Erreur critique de génération RAG : {e}")
        raise e

    try:
        notes_ia = evaluate_rag_response(question, reponse_ia, sources)
        log_to_mlflow(question, reponse_ia, sources, notes_ia)
        
        RAG_ANSWER_RELEVANCE.set(notes_ia.get("answer_relevance", 0.0))
        RAG_FAITHFULNESS.set(notes_ia.get("faithfulness", 0.0))
    except Exception as e:
        print(f" Le système MLOps a échoué (Timeout), mais la réponse a été envoyée au médecin. Erreur : {e}")
        
    return nouvelle_requete, sources