import os
from langchain_google_genai import ChatGoogleGenerativeAI
from rag.retriever import retrieve_documents
from rag.reranker import rerank_documents
from rag.prompt_template import get_clinical_prompt

_llm = None

def ask_clinical_assistant(question: str):
    """Étape 4 : Fait tout le travail et renvoie la réponse de l'IA."""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.0, # 0 = Pas d'hallucination médicale
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    # 1. Cherche 5 documents
    docs = retrieve_documents(question)
    
    # 2. Garde les 3 meilleurs
    best_docs = rerank_documents(question, docs)
    
    # 3. Colle les textes pour faire le contexte
    context_text = "\n\n".join(best_docs)
    
    # 4. Prépare les instructions
    prompt = get_clinical_prompt(question, context_text)
    
    # 5. Gemini génère la réponse
    # ...
    response = _llm.invoke(prompt)
    
    # --- CORRECTION POUR GEMINI ---
    raw_content = response.content
    
    # Si Gemini renvoie une liste de dictionnaires, on extrait juste le texte
    if isinstance(raw_content, list):
        # On fouille dans la liste pour récupérer uniquement le texte
        texte_final = " ".join([item.get("text", "") for item in raw_content if isinstance(item, dict)])
    else:
        # Si c'est déjà un texte normal
        texte_final = str(raw_content)
    # -------------------------------

    print("✅Réponse générée avec succès !")
    print("======================================\n")
    
    # On renvoie le texte pur ET les sources
    return texte_final, best_docs
    