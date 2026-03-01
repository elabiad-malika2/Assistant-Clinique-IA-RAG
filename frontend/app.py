# frontend/app.py

import streamlit as st
import requests
import os
import pandas as pd # Ajout de pandas pour faire un beau tableau

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
    st.title("🩺 CliniQ")
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

# --- BLOCAGE SI NON CONNECTÉ ---
if not st.session_state.token:
    st.title("Bienvenue sur CliniQ")
    st.info("👈 Veuillez vous connecter dans le menu latéral pour utiliser l'assistant et voir votre tableau de bord.")
    st.stop()


# ==========================================
# CRÉATION DES ONGLETS (TABS)
# ==========================================
tab1, tab2 = st.tabs(["💬 Assistant Clinique", "📊 Mon Tableau de Bord"])

# ------------------------------------------
# ONGLET 1 : LE CHATBOT RAG
# ------------------------------------------
with tab1:
    st.title("Dialogue avec l'IA")

    # 1. Afficher l'historique de la discussion en cours
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📚 Voir les sources extraites (Protocole)"):
                    for idx, source in enumerate(msg["sources"], 1):
                        st.caption(f"**Source {idx} :** {source}")

    # 2. Barre de saisie pour une nouvelle question
    if prompt := st.chat_input("Ex: Quels sont les traitements pour..."):
        
        # Affichage immédiat à l'écran
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        payload = {"question": prompt}
        
        with st.chat_message("assistant"):
            with st.spinner("Recherche dans les protocoles..."):
                try:
                    res = requests.post(f"{API_URL}/api/queries/ask", json=payload, headers=headers)
                    
                    if res.status_code == 200:
                        data = res.json()
                        reponse_ia = data.get("reponse", "Erreur de génération.")
                        sources_ia = data.get("sources", [])
                        
                        st.markdown(reponse_ia)
                        
                        if sources_ia:
                            with st.expander("📚 Voir les sources extraites (Protocole)"):
                                for idx, source in enumerate(sources_ia, 1):
                                    st.caption(f"**Source {idx} :** {source}")
                        
                        # Sauvegarde en mémoire
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": reponse_ia, 
                            "sources": sources_ia
                        })
                    else:
                        st.error(f"Erreur API ({res.status_code}) : Veuillez vous reconnecter.")
                except Exception as e:
                    st.error(f"Impossible de contacter le serveur : {e}")

# ------------------------------------------
# ONGLET 2 : LE DASHBOARD (HISTORIQUE BDD)
# ------------------------------------------
with tab2:
    st.title("📊 Tableau de Bord du Médecin")
    st.write("Retrouvez ici l'historique de toutes vos interactions passées avec l'assistant CliniQ.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    try:
        # On appelle la route /history de l'API
        res = requests.get(f"{API_URL}/api/queries/history", headers=headers)
        
        if res.status_code == 200:
            history_data = res.json()
            
            if not history_data:
                st.info("Vous n'avez posé aucune question pour le moment. Allez dans l'onglet Assistant pour commencer !")
            else:
                # 1. Afficher un compteur global
                st.metric(label="Total de vos requêtes RAG", value=len(history_data))
                st.divider()
                
                # 2. Afficher un beau tableau (Dataframe)
                st.subheader("Vue synthétique")
                df_data = []
                for item in history_data:
                    df_data.append({
                        "ID": item.get("id"),
                        "Question posée": item.get("question"),
                        "Aperçu Réponse": str(item.get("reponse", ""))[:120] + "..." # Coupe la réponse pour le tableau
                    })
                
                df = pd.DataFrame(df_data)
                # Affichage propre sans l'index numérique
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # 3. Afficher les détails complets dans des accordéons
                st.subheader("Détail de vos interactions")
                for item in history_data:
                    # Titre de l'accordéon
                    with st.expander(f"Requête #{item.get('id')} : {item.get('question')}"):
                        st.markdown("**Votre question :**")
                        st.info(item.get("question"))
                        
                        st.markdown("**Réponse de l'IA :**")
                        st.success(item.get("reponse"))
        else:
            st.error("Impossible de charger l'historique.")
            
    except Exception as e:
        st.error(f"Erreur de connexion à l'API : {e}")