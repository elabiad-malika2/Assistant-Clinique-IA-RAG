# from fastapi.testclient import TestClient
# from app.main import app
# from app.core.security import get_password_hash,verify_password
# client=TestClient(app)
# def test_auth():
#     response=client.get("/api/queries/history")

#     assert response.status_code == 401

# def test_authRL():
#     password="malika123"
#     hashpassword=get_password_hash(password)
#     verify_passwo=verify_password(password,hashpassword)

#     assert hashpassword !=password
#     assert verify_passwo is True

# from sqlalchemy import *
# from app.db.base import Base
# from sqlalchemy.orm import *



# class User(Base):
#     __tablename__="users"
#     id=Column(Integer,primary_key=True)
#     nom=Column(String,nullable=False)

#     queries=relationship(
#         'Query',
#         back_populates="user"

#     )

# class Query(Base):
#     __tablename__="queries"
#     id=Column(Integer,primary_key=True)
#     query=Column(String,nullable=false)
#     response=Column(String,nullable=False)

#     user=relationship('User',back_populates="queries")

# 

# import streamlit as str

# str.text_input(placeholder="enter user name")


# from pydantic import *

# class userCreate(BaseModel):
#     nom:str
#     email:EmailStr
#     password:str

# class userResponse(BaseModel):
#     id:int
#     nom:str
#     email:EmailStr

#     class config:
#         from_attributes=True


# from fastapi import *
# from app.models.query import Query as dbQuery

# router=APIRouter()


# router.get("/history")
# def getHistory(db=Depends(get_connection()),currentuser:User=Depends(get_user())):
#     response=db.query(dbQuery).filter(currentuser.id==dbQuery.id).all()
#     return response


# tests/test_rag.py

from unittest.mock import MagicMock, patch
from app.services.rag_service import process_and_save_query

@patch("app.services.rag_service.ask_clinical_assistant")
def test_medical_query_processing(mock_ia):
    
  
    mock_db = MagicMock()
    mock_user_id = 1
    question_medecin = "Quel est le traitement ?"
    
    mock_ia.return_value = ("Prenez du Doliprane.", ["Document PDF page 2"])
    


    requete_sauvegardee, sources = process_and_save_query(
        mock_db, 
        mock_user_id, 
        question_medecin
    )

  
    assert requete_sauvegardee.reponse == "Prenez du Doliprane."
    assert sources == ["Document PDF page 2"]
    






