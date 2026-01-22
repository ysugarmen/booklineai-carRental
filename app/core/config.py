from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATA_FILE_PATH: Path = Field(default=ROOT_DIR / "storage" / "data.json")
    LOGGING_LEVEL: str = Field(default="INFO")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

