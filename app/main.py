from fastapi import FastAPI
from app.api.auth_router import router as auth_router
from app.db.session import engine
from app.db.base import Base

# Création des tables dans la BD
from app.models.user import User
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CliniQ", description="Assistant décisionnel clinique RAG")

# Inclusion des routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "CliniQ API est en ligne !"}