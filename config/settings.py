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
    WATSONX_BEARER_TOKEN: str = "eyJraWQiOiIyMDE5MDcyNCIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJJQk1pZC02OTQwMDFIVlFQIiwiaWQiOiJJQk1pZC02OTQwMDFIVlFQIiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiMzIxMzU2N2MtYmM3Yi00MzFlLTk0ZjEtZmYxNDdkODUzNDBkIiwiaWRlbnRpZmllciI6IjY5NDAwMUhWUVAiLCJnaXZlbl9uYW1lIjoiRmxhdmlvIiwiZmFtaWx5X25hbWUiOiJTY2hhbHkiLCJuYW1lIjoiRmxhdmlvIFNjaGFseSIsImVtYWlsIjoiZmxhdmlvLnNjaGFseUBhdXRuZXNzLmNvbSIsInN1YiI6ImZsYXZpby5zY2hhbHlAYXV0bmVzcy5jb20iLCJhdXRobiI6eyJzdWIiOiJmbGF2aW8uc2NoYWx5QGF1dG5lc3MuY29tIiwiaWFtX2lkIjoiSUJNaWQtNjk0MDAxSFZRUCIsIm5hbWUiOiJGbGF2aW8gU2NoYWx5IiwiZ2l2ZW5fbmFtZSI6IkZsYXZpbyIsImZhbWlseV9uYW1lIjoiU2NoYWx5IiwiZW1haWwiOiJmbGF2aW8uc2NoYWx5QGF1dG5lc3MuY29tIn0sImFwaWtleV91dWlkIjoiQXBpS2V5LWE2YTE0M2MyLTkyNDEtNDgzMS1hZDg0LTAxZTI3M2I5YTlmNCIsImFjY291bnQiOnsidmFsaWQiOnRydWUsImJzcyI6IjE5NjM4Yzc1ZGJmMTRiMDZhMjQ1NTE1ZDU5NDYyYzBiIiwiaW1zX3VzZXJfaWQiOiIxNTI1OTUwMCIsImZyb3plbiI6dHJ1ZSwiaXNfZW50ZXJwcmlzZV9hY2NvdW50IjpmYWxzZSwiZW50ZXJwcmlzZV9pZCI6ImVlNTc1YzU3Nzg3NjRkNDA5MTU1YWEzNTc4MGVjOGQxIiwiaW1zIjoiMjY5NTcwMSJ9LCJpYXQiOjE3NzU2ODI3MjUsImV4cCI6MTc3NTY4NjMyNSwiaXNzIjoiaHR0cHM6Ly9pYW0uY2xvdWQuaWJtLmNvbS9pZGVudGl0eSIsImdyYW50X3R5cGUiOiJ1cm46aWJtOnBhcmFtczpvYXV0aDpncmFudC10eXBlOmFwaWtleSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImRlZmF1bHQiLCJhY3IiOjEsImFtciI6WyJwd2QiXX0.ILSWqTV5UR3xtrQvdJnh8d-ZNhZ99H7JNpQ9SU_-LOjc5nf4jAQe7wc8uVA2nPJPiqpumJwaWGLRlq6I4l9nsu6LcyY6ftI6EW5Q-ANkOEC7-Mst6FYKFKvp41jwyS9XSuiyZ_cawa9Sy4dyN5awfYzBGzmbSBr_iDZGiYLasPVj1IHiVV2iFwVC3RRWwLua9Ws7tJLECrRcn99P8lTCoZPA5dnMWDb6CdAUQJS5YUWaKzg5P-Bk2PdstzrtpeeC91UxAAnqwbcBK_ZKVKE1kqD-u_xXBkN_a0hqORoZnwokIVPV0rbL584Ecx08VXaq2vZ8LXyCN0_dXYHP6Dj01w"
    WATSONX_API_KEY: str = "QLnTODyZUT2k8UmYC7V2XIgPK2Ht4BL3hySg45RBEuIF"
    WATSONX_API_KEY_HEADER: str = "x-api-key"
    WATSONX_PROJECT_ID: str = ""
    WHATSAPP_THREAD_MAPPING_PATH: str = "data/whatsapp_thread_mapping.json"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
