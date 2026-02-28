from typing import List
from fastapi import APIRouter, Depends
from app.models.query import Query as DBQuery
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user # get_current_user vérifie le Token !
from app.schemas.query_schema import QueryRequest, QueryResponse
from app.models.user import User
from app.services.rag_service import process_and_save_query

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest, db: Session = Depends(get_db), 
                 current_user: User = Depends(get_current_user)):
    
    # Si le token JWT est invalide, FastAPI bloque l'accès automatiquement.
    # Si c'est bon, on traite la question
    saved_query, sources = process_and_save_query(db, current_user.id, request.question)
    
    # On renvoie la réponse formattée pour le Frontend
    return {
        "id": saved_query.id,
        "question": saved_query.query,
        "reponse": saved_query.reponse,
        "sources": sources
    }

# app/api/query_router.py (à ajouter à la fin du fichier)

@router.get("/history", response_model=List[QueryResponse])
def get_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) ):
    
    # On cherche toutes les requêtes qui appartiennent à cet utilisateur
    historique = db.query(DBQuery).filter(DBQuery.user_id == current_user.id).order_by(DBQuery.created_at.desc()).all()
    
    # On formate la réponse pour qu'elle corresponde au QueryResponse
    resultats = []
    for req in historique:
        resultats.append({
            "id": req.id,
            "question": req.query,
            "reponse": req.reponse,
            "sources": [] # Les sources ne sont pas stockées dans la DB actuelle, on renvoie vide pour l'historique
        })
        
    return resultats