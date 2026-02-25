# rag/vector_store.py

import os
import chromadb
from typing import List
from langchain_core.documents import Document

# Configuration des chemins et du nom de la base
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
COLLECTION_NAME = "cliniq_medical_docs"

def get_chroma_collection():
    """
    Initialise ou récupère la collection ChromaDB.
    Cette fonction est appelée automatiquement par les autres fonctions.
    """
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"} # Optimisé pour la similarité sémantique
    )
    return collection

def add_documents_to_chroma(documents: List[Document], embeddings: List[List[float]]):
    """
    Prend les documents (chunks) et leurs vecteurs (embeddings) 
    et les sauvegarde directement dans ChromaDB.
    """
    if not documents:
        print("⚠️ Aucun document à ajouter.")
        return

    collection = get_chroma_collection()
    
    ids = []
    texts = []
    metadatas = []

    for i, doc in enumerate(documents):
        # Création d'un ID unique basé sur le contenu
        chunk_id = f"chunk_{i}_{hash(doc.page_content)}"
        ids.append(chunk_id)
        texts.append(doc.page_content)
        
        # Nettoyage des métadonnées (Chroma n'accepte que des strings, ints ou floats)
        clean_meta = {k: str(v) for k, v in doc.metadata.items()} if doc.metadata else {"source": "unknown"}
        metadatas.append(clean_meta)

    print(f" Sauvegarde de {len(texts)} chunks dans ChromaDB...")
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    print(" Sauvegarde terminée avec succès !")

def search_similar_in_chroma(query_embedding: List[float], top_k: int = 3):
    """
    Recherche les 'top_k' chunks les plus proches de la question posée.
    """
    collection = get_chroma_collection()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results