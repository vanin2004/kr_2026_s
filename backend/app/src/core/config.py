from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgres://postgres:password@db:5432/tutorapp"
    SECRET_KEY: str = "secret-key-for-jwt-validation-if-needed"
    KEYCLOAK_URL: str = "http://keycloak:8080"
    FCM_KEY_PATH: str = "/app/firebase-key.json"
    
    class Config:
        env_file = ".env"

settings = Settings()
