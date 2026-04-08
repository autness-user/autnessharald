from __future__ import annotations

from typing import Any, Dict, Tuple

import requests

from config.settings import settings


class WatsonxThreadsService:
    def __init__(self) -> None:
        if not settings.WATSONX_THREADS_API_BASE_URL:
            raise ValueError("WATSONX_THREADS_API_BASE_URL nao configurado")

        self.base_url = settings.WATSONX_THREADS_API_BASE_URL.rstrip("/")
        self.path_template = settings.WATSONX_THREADS_DELETE_PATH_TEMPLATE
        self.timeout_seconds = settings.WATSONX_THREADS_TIMEOUT_SECONDS

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if settings.WATSONX_BEARER_TOKEN:
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
