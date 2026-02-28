# app/models/query.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base

class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    reponse = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)    
    user_id = Column(Integer, ForeignKey("users.id"))