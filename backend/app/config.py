from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str  # Mudou de GEMINI para GROQ

    class Config:
        env_file = ".env"

settings = Settings()