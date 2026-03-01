# rag/embedding.py

from sentence_transformers import SentenceTransformer
from typing import List

# Choix du modèle performant pour le français médical
MODEL_NAME = "dangvantuan/sentence-camembert-base"

# Variable globale pour stocker le modèle en mémoire (Lazy Loading)
_model = None

def get_embedding_model():
    """
    Charge le modèle d'embedding s'il n'est pas déjà chargé.
    """
    global _model
    if _model is None:
        print(f" Chargement du modèle d'embedding : {MODEL_NAME}...")
        _model = SentenceTransformer(MODEL_NAME)
        print(" Modèle chargé avec succès !")
    return _model

def embed_text(text: str) -> List[float]:
    """
    Convertit un seul texte simple en vecteur (embedding).
    """
    model = get_embedding_model()
    # encode() renvoie un tableau numpy, on le convertit en liste python standard
    embedding = model.encode(text)
    return embedding.tolist()

def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Convertit une liste de textes en vecteurs (idéal pour le chunking).
    Affiche une barre de progression.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()