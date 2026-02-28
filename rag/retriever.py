from typing import List
from rag.embedding import embed_text
from rag.vector_store import search_similar_in_chroma

def retrieve_documents(query: str) -> List[str]:
    """Étape 1 : Va chercher les 5 passages les plus proches de la question."""
    query_emb = embed_text(query)
    results = search_similar_in_chroma(query_emb, top_k=5)
    
    # On récupère juste la liste des textes trouvés
    documents = results.get("documents", [[]])[0]
    return documents