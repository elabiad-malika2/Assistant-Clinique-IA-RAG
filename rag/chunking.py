# rag/chunking.py

from typing import List
from langchain_core.documents import Document # Import mis à jour (langchain.schema est obsolète)
from langchain_text_splitters import MarkdownHeaderTextSplitter

MAX_CHUNK_SIZE = 1200  # Taille idéale pour les embeddings
MIN_CHUNK_SIZE = 200

def split_conserve_tables(text: str) -> List[str]:
    """
    Découpe le contenu en blocs (paragraphes ou tableaux) 
    sans jamais couper un tableau Markdown au milieu.
    """
    chunks = []
    buffer = []
    in_table = False

    lines = text.split("\n")

    for line in lines:
        # Détection d'une ligne de tableau Markdown
        if "|" in line:
            in_table = True
            buffer.append(line)
        elif line.strip() == "":
            # Une ligne vide signifie la fin d'un paragraphe ou d'un tableau
            if buffer:
                chunks.append("\n".join(buffer).strip())
                buffer = []
            in_table = False
        else:
            # Ligne de texte normal
            buffer.append(line)

    # Vider le reste du buffer
    if buffer:
        chunks.append("\n".join(buffer).strip())

    return chunks


def chunk_markdown_text(markdown_text: str) -> List[Document]:
    """
    Applique un chunking hiérarchique basé sur les titres Markdown,
    puis redécoupe les très grandes sections intelligemment.
    """
    print(" Début du chunking hiérarchique...")

    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]

    # Attention : MarkdownHeaderTextSplitter ne prend pas de chunk_overlap
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    header_sections = splitter.split_text(markdown_text)

    final_chunks = []

    for section in header_sections:
        content = section.page_content.strip()
        metadata = section.metadata

        # Si la section est de bonne taille → on la garde telle quelle
        if len(content) <= MAX_CHUNK_SIZE:
            final_chunks.append(Document(page_content=content, metadata=metadata))
        else:
            # Découpage interne intelligent (paragraphes / tableaux)
            sub_parts = split_conserve_tables(content)

            buffer = ""
            for i, part in enumerate(sub_parts):
                # Si l'ajout de la partie ne dépasse pas la taille max
                if len(buffer) + len(part) < MAX_CHUNK_SIZE:
                    buffer = buffer + "\n\n" + part if buffer else part
                else:
                    # Le buffer est plein, on sauvegarde le chunk
                    final_chunks.append(Document(page_content=buffer.strip(), metadata=metadata))
                    
                    # GESTION DE L'OVERLAP (Chevauchement)
                    # On initialise le nouveau buffer avec la partie actuelle (qui n'a pas pu rentrer)
                    buffer = part
                    
                    # Pour assurer un contexte (overlap), si la partie précédente n'était pas un tableau, 
                    # on pourrait la rajouter, mais ici garder le 'part' actuel comme base est un bon compromis 
                    # pour ne pas casser la logique des tableaux.

            # Ne pas oublier le dernier buffer restant
            if buffer:
                final_chunks.append(Document(page_content=buffer.strip(), metadata=metadata))

    print(f" Chunking terminé : {len(final_chunks)} chunks créés.")
    return final_chunks