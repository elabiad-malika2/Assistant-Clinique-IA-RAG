from sqlalchemy import Column


def get_clinical_prompt(question: str, context: str) -> str:
    prompt = f"""Tu es CliniQ, un assistant décisionnel clinique expert développé par ProtoCare.
Tu dois répondre en te basant PRIORITAIREMENT sur le CONTEXTE MÉDICAL fourni.

RÈGLES :
1. Si le contexte contient des éléments utiles (même partiels), utilise-les pour construire une réponse structurée.
2. Tu peux reformuler et synthétiser.
3. Si l'information est partielle, précise-le.
4. Si aucune information pertinente n’est trouvée dans le contexte, répond :
"Les protocoles actuels ne contiennent pas cette information."

CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE :
"""
    return prompt


# router.get("/history"):
# def get_Hisotrique(db=Depends(get_db),current_user:User=Depends(get_user_connect)):
#     historique=db.query(Query).filter(Query.userèid==current_user.id)

#     return historique

# class Query():
#     __tablename__="queries"
#     id=Column(Integer,primary_key=True)
#     reponse=Column(String,nullable=Flase)
#     question=Column(String,nullable=Flase)
#     user_id=Column(Integer,ForeignKey('User.id'))

@patch("api.url")
def tesLLM(mockia):

    db=MagicMock()
    user=1
    question="Comment traiter le maux de tete"

    mockia.return_value=""