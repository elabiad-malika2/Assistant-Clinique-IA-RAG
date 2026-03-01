# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Ajouter pour Postgres
    POSTGRES_USER: str =None
    POSTGRES_PASSWORD: str=None
    POSTGRES_DB: str=None

    # Ajouter pour parsing
    LLAMA_CLOUD_API_KEY : str=None

    GOOGLE_API_KEY:str=None

    class Config:
        env_file = ".env"

settings = Settings()