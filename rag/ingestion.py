# rag/ingestion.py
import os
from llama_parse import LlamaParse
from app.core.config import settings 
def parse_pdf_to_markdown(pdf_path: str) -> str:
  
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Le fichier {pdf_path} est introuvable.")

    print(f"📄 Début de l'analyse avec LlamaParse pour : {pdf_path}")
    
    # Configuration du parser
    parser = LlamaParse(
        api_key=settings.LLAMA_CLOUD_API_KEY,
        result_type="markdown",  
        verbose=True
    )
    
    documents = parser.load_data(pdf_path)
    
    full_markdown_text = "\n\n".join([doc.text for doc in documents])

    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "manuel_complet.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_markdown_text)
    
    print("Conversion en Markdown réussie !")
    return full_markdown_text