from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    groq_transcription_model: str = "whisper-large-v3-turbo"
    luna_api_key: str
    luna_url_base: str
    luna_model: str
    request_timeout_seconds: float = 45.0
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    allowed_origin_regex: str | None = r"https://[a-z0-9-]+-5173\.app\.github\.dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("luna_model", mode="before")
    @classmethod
    def normalize_luna_model(cls, value: str) -> str:
        return value.removeprefix("litellm/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
