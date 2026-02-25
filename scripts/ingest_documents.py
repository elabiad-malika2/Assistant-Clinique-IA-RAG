import sys
import os

# Permet à Python de trouver le dossier 'rag' depuis le dossier 'scripts'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.ingestion import parse_pdf_to_markdown
from rag.chunking import chunk_markdown_text
from rag.embedding import embed_batch, embed_text
from rag.vector_store import add_documents_to_chroma, search_similar_in_chroma

def main():
    # 1. Chemin vers votre fichier PDF (à adapter si besoin)
    # Ce code pointe vers "cliniq/data/protocole_test.pdf"
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pdf_path = os.path.join(base_dir, "data", "protocole_test.pdf")
    
    if not os.path.exists(pdf_path):
        print(f" Erreur : Fichier introuvable -> {pdf_path}")
        print("Veuillez créer un dossier 'data' à la racine et y placer 'protocole_test.pdf'.")
        return

    try:
        # ÉTAPE 1 : INGESTION (Conversion du PDF en Markdown avec LlamaParse)
        print("\n--- ÉTAPE 1 : INGESTION ---")
        markdown_content = parse_pdf_to_markdown(pdf_path)
        
        # ÉTAPE 2 : CHUNKING (Découpage en conservant les tableaux et titres)
        print("\n--- ÉTAPE 2 : CHUNKING ---")
        chunks = chunk_markdown_text(markdown_content)
        
        if not chunks:
            print("❌ Erreur : Le document semble vide, aucun chunk généré.")
            return

        # ÉTAPE 3 : EMBEDDINGS (Création des vecteurs avec Hugging Face)
        print("\n--- ÉTAPE 3 : EMBEDDINGS ---")
        texts_to_embed = [chunk.page_content for chunk in chunks]
        embeddings = embed_batch(texts_to_embed)
        
        # ÉTAPE 4 : STOCKAGE VECTORIEL (Sauvegarde dans ChromaDB)
        print("\n--- ÉTAPE 4 : STOCKAGE DANS CHROMADB ---")
        add_documents_to_chroma(documents=chunks, embeddings=embeddings)

        print("\n🎉 INGESTION TERMINÉE AVEC SUCCÈS ! 🎉")
        
        # ÉTAPE 5 : TEST DE RECHERCHE RAPIDE (Pour vérifier que le RAG fonctionne)
        print("\n--- TEST DE RECHERCHE ---")
        question = "Quels sont les traitements recommandés ?"
        print(f"Question testée : '{question}'")
        
        query_embedding = embed_text(question)
        results = search_similar_in_chroma(query_embedding, top_k=1)
        
        # Affichage du résultat s'il y en a un
        if results and results['documents'] and results['documents'][0]:
            print("\n✅ Meilleur résultat trouvé (extrait) :")
            print(f"{results['documents'][0][0][:300]}...") # Affiche les 300 premiers caractères
        else:
            print("Aucun résultat trouvé dans la base.")

    except Exception as e:
        print(f"\n❌ Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    main()