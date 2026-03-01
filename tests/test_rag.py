# tests/test_rag.py

from rag.prompt_template import get_clinical_prompt
from rag.chunking import chunk_markdown_text


def test_prompt_generation():
    question = "Quel est le traitement recommandé ?"
    context = "Paracétamol 1g toutes les 6 heures."

    prompt_final = get_clinical_prompt(question, context)

    assert "CliniQ" in prompt_final
    assert "RÈGLE" in prompt_final  # plus robuste que chercher un mot précis
    assert question in prompt_final
    assert context in prompt_final


def test_chunking_logic():
    texte_md = "# Titre 1\nVoici un texte.\n## Sous-titre\nAutre texte."
    chunks = chunk_markdown_text(texte_md)

    assert len(chunks) > 0
    assert "h1" in chunks[0].metadata or "h2" in chunks[1].metadata