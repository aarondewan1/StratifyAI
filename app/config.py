from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    """Environment-backed settings for StratifyAI."""
    # Required API keys
    openai_api_key: str
    serper_api_key: str

    # Optional flags
    debug: bool = False

    # Instruct Pydantic to load a local .env file for development
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Instantiate settings (will read from environment or .env)
settings = Settings()

# Initialize the OpenAI LLM using the loaded API key
from langchain_openai import ChatOpenAI

LLM = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    openai_api_key=settings.openai_api_key,
)
