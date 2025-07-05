from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    openai_api_key: str = Field(default=None, alias="OPENAI_API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")
    serper_api_key: str = Field(default=None, alias="SERPER_API_KEY")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Create settings instance
settings = Settings()

# Initialize LLM with API key from settings
LLM = ChatOpenAI(
    temperature=0, 
    model="gpt-4o",
    openai_api_key=settings.openai_api_key
)
