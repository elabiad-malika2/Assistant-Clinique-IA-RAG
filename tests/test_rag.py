# tests/test_rag.py

from rag.prompt_template import get_clinical_prompt
from rag.chunking import chunk_markdown_text

def test_prompt_generation():
    """Vérifie que le prompt médical est bien formaté avec les règles strictes"""
    question = "Quel est le traitement recommandé ?"
    context = "Paracétamol 1g toutes les 6 heures."
    
    prompt_final = get_clinical_prompt(question, context)
    
    # On vérifie que les éléments clés sont bien dans le prompt
    assert "CliniQ" in prompt_final
    assert "UNIQUEMENT" in prompt_final # La consigne de sécurité anti-hallucination
    assert question in prompt_final
    assert context in prompt_final

def test_chunking_logic():
    """Vérifie que la logique de découpage des protocoles fonctionne"""
    texte_md = "# Titre 1\nVoici un texte de test.\n## Sous-titre\nUn autre texte."
    chunks = chunk_markdown_text(texte_md)
    
    assert len(chunks) > 0
    # On vérifie que le chunking garde bien les métadonnées (les titres)
    assert "h1" in chunks[0].metadata or "h2" in chunks[1].metadata