from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_SPREADSHEET_ID: str = ""
    GOOGLE_CREDENTIALS_PATH: str = "credentials/credentials.json"
    GOOGLE_TOKEN_PATH: str = "credentials/token.json"
    GOOGLE_API_KEY: Optional[str] = None

    APP_NAME: str = "Google Sheets API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_HEADERS: List[str] = Field(default_factory=lambda: ["*"])

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
