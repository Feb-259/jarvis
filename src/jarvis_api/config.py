
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JARVIS"
    environment: str = "development"
    database_url: str = "postgresql://jarvis:jarvis_dev_only@localhost:5432/jarvis"

    llm_provider: str = "mock"
    ollama_model: str = "qwen2.5:3b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: float = 120.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
