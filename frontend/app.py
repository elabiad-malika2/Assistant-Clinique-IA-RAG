# frontend/app.py

import streamlit as st
import requests
import os

# On récupère l'URL de l'API (définie dans le docker-compose)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CliniQ - Assistant IA", page_icon="🩺", layout="wide")

# Initialisation des variables de session (mémoire du navigateur)
if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE (LOGIN) ---
with st.sidebar:
    st.title(" CliniQ")
    st.write("Assistant décisionnel clinique")
    st.divider()

    if not st.session_state.token:
        st.subheader("Connexion requise")
        email = st.text_input("Email", value="test@hopital.fr")
        password = st.text_input("Mot de passe", type="password", value="mon_mot_de_passe")
        
        if st.button("Se connecter", use_container_width=True):
            # Appel à l'API FastAPI pour se connecter
            response = requests.post(
                f"{API_URL}/api/auth/login",
                data={"username": email, "password": password}
            )
            
            if response.status_code == 200:
                st.session_state.token = response.json().get("access_token")
                st.success("Connexion réussie !")
                st.rerun() # Rafraîchit la page
            else:
                st.error("Identifiants incorrects.")
    else:
        st.success("Vous êtes connecté.")
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.token = None
            st.session_state.messages = []
            st.rerun()

# --- FENÊTRE PRINCIPALE (CHATBOT) ---
st.title("Dialogue avec l'IA")

# Si l'utilisateur n'est pas connecté, on bloque l'accès
if not st.session_state.token:
    st.info("Veuillez vous connecter dans le menu latéral pour utiliser l'assistant.")
    st.stop()

# 1. Afficher l'historique des messages dans l'écran
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Si c'est une réponse de l'IA, on affiche les sources dans un menu déroulant
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Voir les sources extraites (Protocole)"):
                for idx, source in enumerate(msg["sources"], 1):
                    st.caption(f"**Source {idx} :** {source}")

# 2. La barre de saisie pour poser une nouvelle question
if prompt := st.chat_input("Ex: Quels sont les traitements pour..."):
    
    # On ajoute la question de l'utilisateur à l'écran
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # On appelle l'API FastAPI avec le Token d'authentification !
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    payload = {"question": prompt}
    
    with st.chat_message("assistant"):
        with st.spinner("Recherche dans les protocoles..."):
            try:
                # Requête POST vers notre route RAG sécurisée
                res = requests.post(f"{API_URL}/api/queries/ask", json=payload, headers=headers)
                
                if res.status_code == 200:
                    data = res.json()
                    reponse_ia = data.get("reponse", "Erreur de génération.")
                    sources_ia = data.get("sources", [])
                    
                    # On affiche la réponse
                    st.markdown(reponse_ia)
                    
                    # On affiche les sources
                    if sources_ia:
                        with st.expander(" Voir les sources extraites (Protocole)"):
                            for idx, source in enumerate(sources_ia, 1):
                                st.caption(f"**Source {idx} :** {source}")
                    
                    # On sauvegarde dans l'historique de l'écran
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": reponse_ia, 
                        "sources": sources_ia
                    })
                else:
                    st.error(f"Erreur API ({res.status_code}) : Veuillez vous reconnecter.")
            except Exception as e:
                st.error(f"Impossible de contacter le serveur : {e}")