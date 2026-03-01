from sqlalchemy.orm import Session
from app.models.query import Query
from rag.rag_pipeline import ask_clinical_assistant
# from mlops.deepeval_metrics import evaluate_rag_response
# from app.services.mlflow_service import log_to_mlflow

from monitoring.prometheus_metrics import (
    RAG_REQUESTS_TOTAL, 
    RAG_ERRORS_TOTAL, 
    RAG_ANSWER_RELEVANCE, 
    RAG_FAITHFULNESS
)

def process_and_save_query(db: Session, user_id: int, question: str):
    """Fait appel à l'IA et sauvegarde le résultat dans PostgreSQL."""

    # +1 au compteur des requêtes posées !
    RAG_REQUESTS_TOTAL.inc()
    
    try:
        # 1. On appelle notre IA (Le Chef d'Orchestre)
        reponse_ia, sources = ask_clinical_assistant(question)
        
        # 2. On sauvegarde dans la table 'queries' de la base de données
        nouvelle_requete = Query(
            query=question,
            reponse=reponse_ia,
            user_id=user_id # On lie la question au médecin connecté !
        )
        db.add(nouvelle_requete)
        db.commit()
        db.refresh(nouvelle_requete)

        # # 3. MLOPS : On note la réponse avec DeepEval
        # notes_ia = evaluate_rag_response(question, reponse_ia, sources)
        
        # # 4. MLOPS : On envoie tout au tableau de bord MLflow
        # log_to_mlflow(question, reponse_ia, sources, notes_ia)

        # # 5. MONITORING : On met à jour les jauges de qualité pour Prometheus !
        # RAG_ANSWER_RELEVANCE.set(notes_ia.get("answer_relevance", 0.0))
        # RAG_FAITHFULNESS.set(notes_ia.get("faithfulness", 0.0))

    except Exception as e:
        # +1 au compteur des erreurs si l'IA ou la DB plante !
        RAG_ERRORS_TOTAL.inc()
        print(f" Erreur critique du RAG : {e}")
        raise e
        
    return nouvelle_requete, sources