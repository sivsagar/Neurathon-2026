"""Configuration management for The Smart Companion."""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # LLM Configuration
    gemini_api_key: str
    model_name: str = "gemini-2.0-flash"
    max_tokens: int = 150
    temperature: float = 0.7
    
    # Performance Targets
    max_response_time_seconds: int = 5
    
    # Database
    database_path: str = "data/smart_companion.db"
    
    # Step Validation Rules
    max_step_seconds: int = 10
    simplification_max_seconds: int = 5
    
    # Privacy
    strip_personal_info: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
