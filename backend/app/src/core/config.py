from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgres://postgres:password@db:5432/tutorapp"
    SECRET_KEY: str = "secret-key-for-jwt-validation-if-needed"

    # ── Keycloak ───────────────────────────────────────────────
    KEYCLOAK_URL: str = "http://keycloak:8080/auth"
    KEYCLOAK_REALM: str = "tutorapp"
    KEYCLOAK_ADMIN_USER: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"

    FCM_KEY_PATH: str = "/app/firebase-key.json"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
