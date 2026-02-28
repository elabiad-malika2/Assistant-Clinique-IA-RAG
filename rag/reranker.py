from sentence_transformers import CrossEncoder
from typing import List

_reranker_model = None

def rerank_documents(query: str, documents: List[str]) -> List[str]:
    """Étape 2 : Donne une note sur 100 à chaque passage et garde les 3 meilleurs."""
    global _reranker_model
    if _reranker_model is None:
        _reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    if not documents:
        return []
        
    # On crée des paires [Question, Passage] pour que le modèle les note
    pairs = [[query, doc] for doc in documents]
    scores = _reranker_model.predict(pairs)
    
    # On trie du meilleur score au pire
    doc_score_pairs = list(zip(documents, scores))
    doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
    
    # On garde les 3 meilleurs textes
    best_docs = [doc for doc, score in doc_score_pairs[:3]]
    return best_docs