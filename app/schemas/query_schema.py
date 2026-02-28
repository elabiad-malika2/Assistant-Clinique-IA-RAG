from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    id: int
    question: str
    reponse: str
    sources: List[str] 