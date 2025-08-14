from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional
import os

# Cargar .env desde la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

print("DEBUG MONGO_URI:", os.getenv("MONGO_URI"))

class Settings(BaseSettings):
    MONGO_URI: Optional[str] = None
    MONGO_DB_NAME: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = None
    FIREBASE_CREDENTIALS: str = "app/firebase_credentials.json"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
