import os
from langchain_google_genai import ChatGoogleGenerativeAI
from rag.retriever import retrieve_documents
from rag.reranker import rerank_documents
from rag.prompt_template import get_clinical_prompt

_llm = None

def ask_clinical_assistant(question: str):
    """Fait tout le travail (RAG) et renvoie la réponse de l'IA."""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", 
            temperature=0.1,          
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    print(f"\n QUESTION : {question}")
        
    # 1 retrieval 
    docs = retrieve_documents(question, top_k=5)
    
    if not docs:
        print(" Aucun document trouvé dans la base.")
        return "Je suis désolé, mais les protocoles actuels ne contiennent aucune information à ce sujet.", []
    
    # 2 reranking 
    best_docs = rerank_documents(question, docs, top_n=3)
    
    # 3 prompt 
    context_text = "\n\n---\n\n".join(best_docs)
    prompt = get_clinical_prompt(question, context_text)
    
    # 4 generation 
    print(" Gemini réfléchit...")
    response = _llm.invoke(prompt)
    
    # 5 nattoyage de la reponse 
    raw_content = response.content
    if isinstance(raw_content, list):
        texte_final = " ".join([item.get("text", "") for item in raw_content if isinstance(item, dict)])
    else:
        texte_final = str(raw_content)

    print(" Réponse générée avec succès !\n")
    
    return texte_final, best_docs