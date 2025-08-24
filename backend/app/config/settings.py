from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "travel_agent"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "travel-agent-secret-key-change-in-production"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ]
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"

settings = Settings()
