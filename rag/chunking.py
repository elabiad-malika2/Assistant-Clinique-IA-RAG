# rag/chunking.py

from typing import List
from langchain_core.documents import Document 
from langchain_text_splitters import MarkdownHeaderTextSplitter

MAX_CHUNK_SIZE = 1200  
MIN_CHUNK_SIZE = 200

def split_conserve_tables(text: str) -> List[str]:
    
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
    print(" Début du chunking hiérarchique...")

    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    header_sections = splitter.split_text(markdown_text)

    final_chunks = []

    for section in header_sections:
        content = section.page_content.strip()
        metadata = section.metadata

        if len(content) <= MAX_CHUNK_SIZE:
            final_chunks.append(Document(page_content=content, metadata=metadata))
        else:
            sub_parts = split_conserve_tables(content)

            buffer = ""
            for i, part in enumerate(sub_parts):
                if len(buffer) + len(part) < MAX_CHUNK_SIZE:
                    buffer = buffer + "\n\n" + part if buffer else part
                else:
                    final_chunks.append(Document(page_content=buffer.strip(), metadata=metadata))
                    
                    
                    buffer = part
                    
                    
            if buffer:
                final_chunks.append(Document(page_content=buffer.strip(), metadata=metadata))

    print(f" Chunking terminé : {len(final_chunks)} chunks créés.")
    return final_chunks