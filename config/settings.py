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

    WATSONX_THREADS_API_BASE_URL: str = "https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/dbf3a3d1-2d3d-4474-a5fe-cc39180b9e5a"
    WATSONX_THREADS_DELETE_PATH_TEMPLATE: str = "/v1/threads/{thread_id}"
    WATSONX_THREADS_TIMEOUT_SECONDS: int = 30
    WATSONX_BEARER_TOKEN: str = ""
    WATSONX_API_KEY: str = "wLCUuO5vplFXoe4Xc6Gr777YL0EpYEJS5eJPH_QL_lld"
    WATSONX_API_KEY_HEADER: str = "x-api-key"
    WATSONX_PROJECT_ID: str = ""
    WHATSAPP_THREAD_MAPPING_PATH: str = "data/whatsapp_thread_mapping.json"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
