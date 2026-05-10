from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "TxGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/txguard"
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ML Models
    MODEL_DIR: Optional[str] = None
    
    # Secrets
    SECRET_KEY: str = "supersecretkey"
    
    # ChromaDB
    CHROMA_PATH: str = "./data/chroma_db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
