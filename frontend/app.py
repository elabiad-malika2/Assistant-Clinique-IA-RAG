# frontend/app.py

import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="CliniQ - Assistant IA", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bare login.register
with st.sidebar:
    st.title(" CliniQ")
    st.write("Assistant décisionnel clinique")
    st.divider()

    if not st.session_state.token:
        auth_mode = st.radio("Accès au service", ["Se connecter", "Créer un compte"], horizontal=True)
        st.divider()

        if auth_mode == "Se connecter":
            st.subheader("Connexion")
            email = st.text_input("Email", value="test@hopital.fr")
            password = st.text_input("Mot de passe", type="password", value="mon_mot_de_passe")
            
            if st.button("Se connecter", use_container_width=True):
                response = requests.post(
                    f"{API_URL}/api/auth/login",
                    data={"username": email, "password": password}
                )
                
                if response.status_code == 200:
                    st.session_state.token = response.json().get("access_token")
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
                    
        else: 
            st.subheader("Nouveau Médecin")
            new_username = st.text_input("Nom / Prénom (ex: Dr. Dupont)")
            new_email = st.text_input("Email professionnel")
            new_password = st.text_input("Mot de passe", type="password")
            confirm_password = st.text_input("Confirmez le mot de passe", type="password")
            
            if st.button("S'inscrire", use_container_width=True):
                if new_password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas.")
                elif not new_username or not new_email or not new_password:
                    st.warning("Veuillez remplir tous les champs.")
                else:
                    payload = {
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                        "role": "doctor"
                    }
                    res = requests.post(f"{API_URL}/api/auth/register", json=payload)
                    
                    if res.status_code == 200:
                        st.success("Compte créé avec succès ! Sélectionnez 'Se connecter' pour accéder au service.")
                    elif res.status_code == 400:
                        st.error(f"Erreur : {res.json().get('message', 'Cet email est déjà utilisé.')}")
                    else:
                        st.error("Une erreur s'est produite lors de l'inscription.")

    else:
        st.success("Vous êtes connecté.")
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.token = None
            st.session_state.messages = []
            st.rerun()

# --- BLOCAGE SI NON CONNECTÉ ---
if not st.session_state.token:
    st.title("Bienvenue sur CliniQ")
    st.info(" Veuillez vous connecter ou créer un compte dans le menu latéral pour utiliser l'assistant.")
    st.stop()



tab1, tab2 = st.tabs(["Assistant Clinique", "Mon Tableau de Bord"])


with tab1:
    st.title("Dialogue avec l'IA")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander(" Voir les sources extraites (Protocole)"):
                    for idx, source in enumerate(msg["sources"], 1):
                        st.caption(f"**Source {idx} :** {source}")

    if prompt := st.chat_input("Ex: Quels sont les traitements recommandés pour..."):
        
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
                            with st.expander("Voir les sources extraites (Protocole)"):
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

with tab2:
    st.title(" Tableau de Bord du Médecin")
    st.write("Retrouvez ici l'historique de toutes vos interactions passées avec l'assistant CliniQ.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    try:
        res = requests.get(f"{API_URL}/api/queries/history", headers=headers)
        
        if res.status_code == 200:
            history_data = res.json()
            
            if not history_data:
                st.info("Vous n'avez posé aucune question pour le moment. Allez dans l'onglet Assistant pour commencer !")
            else:
                # 1. Afficher un compteur global
                st.metric(label="Total de vos requêtes RAG", value=len(history_data))
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