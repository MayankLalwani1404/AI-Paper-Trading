from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Paper Trading Backend"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()
