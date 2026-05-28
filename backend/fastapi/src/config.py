"""
Configuration module for FastAPI application
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://tutordb_user:tutordb_pass@postgres:5432/tutor_platform_db"
    
    # Keycloak
    keycloak_url: str = "http://keycloak:8080"
    keycloak_realm: str = "tutor-platform"
    keycloak_client_id: str = "tutor-api"
    keycloak_client_secret: str = "your-client-secret"
    
    # JWT
    jwt_secret: str = "your-super-secret-jwt-key-change-me-in-production"
    
    # API
    api_title: str = "Tutor Platform API"
    api_version: str = "1.0.0"
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
