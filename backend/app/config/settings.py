from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    MONGODB_URL: str = "mongodb+srv://ayushgupta4897:lTg0uaOsJ0paEREb@zyushg.vwzgohd.mongodb.net/?retryWrites=true&w=majority&appName=zyushg"
    DATABASE_NAME: str = "travel_agent"
    
    # OpenAI
    OPENAI_API_KEY: str = "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"
    OPENAI_MODEL: str = "gpt-4o"
    
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "travel-agent-secret-key-change-in-production"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://travel-agent-demo.vercel.app"
    ]
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"

settings = Settings()
