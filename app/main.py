from fastapi import FastAPI
from app.api.auth_router import router as auth_router
from app.api.query_router import router as query_router
from app.db.session import engine
from app.db.base import Base
import mlflow 
import os
from prometheus_fastapi_instrumentator import Instrumentator

# Création des tables dans la BD
from app.models.user import User
Base.metadata.create_all(bind=engine)


# MLflow va surveiller LangChain automatiquement en arrière-plan
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
mlflow.langchain.autolog()

app = FastAPI(title="CliniQ", description="Assistant décisionnel clinique RAG")

# Inclusion des routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

app.include_router(query_router, prefix="/api/queries", tags=["IA & RAG"])

Instrumentator().instrument(app).expose(app)



@app.get("/health", tags=["Monitoring"])
def health_check():

    return {"status": "ok", "service": "CliniQ API", "version": "1.0.0"}

@app.get("/")
def root():
    return {"message": "CliniQ API est en ligne !"}