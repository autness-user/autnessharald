from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

import requests

from app.utils.logger import get_logger
from config.settings import settings


logger = get_logger(__name__)


class WatsonxThreadsService:
    def __init__(self) -> None:
        if not settings.WATSONX_THREADS_API_BASE_URL:
            raise ValueError("WATSONX_THREADS_API_BASE_URL nao configurado")

        self.base_url = settings.WATSONX_THREADS_API_BASE_URL.rstrip("/")
        self.path_template = settings.WATSONX_THREADS_DELETE_PATH_TEMPLATE
        self.timeout_seconds = settings.WATSONX_THREADS_TIMEOUT_SECONDS
        self.api_key = settings.WATSONX_API_KEY
        self.access_token: str | None = None
        self.token_expiry: datetime | None = None

    def _get_iam_token(self) -> str:
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        if not self.api_key:
            raise ValueError("WATSONX_API_KEY nao configurado para obter token IAM")

        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key,
            },
            timeout=30,
        )
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)

        logger.info("Token IAM obtido com sucesso")
        return self.access_token

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self._get_iam_token()}"
        elif settings.WATSONX_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {settings.WATSONX_BEARER_TOKEN}"

        if settings.WATSONX_API_KEY:
            headers[settings.WATSONX_API_KEY_HEADER] = settings.WATSONX_API_KEY

        if settings.WATSONX_PROJECT_ID:
            headers["X-Project-Id"] = settings.WATSONX_PROJECT_ID

        return headers

    def delete_thread(self, thread_id: str, channel: str, soft_delete: bool) -> Tuple[int, Dict[str, Any]]:
        path = self.path_template.format(thread_id=thread_id)
        url = f"{self.base_url}{path}"

        payload = {
            "channel": channel,
            "soft_delete": soft_delete,
        }

        response = requests.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout_seconds,
        )

        try:
            body = response.json()
        except ValueError:
            body = {"raw": response.text}

        return response.status_code, body
