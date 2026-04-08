from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from config.settings import settings


class WhatsAppThreadMappingService:
    def __init__(self) -> None:
        self.mapping_path = Path(settings.WHATSAPP_THREAD_MAPPING_PATH)

    def _ensure_parent(self) -> None:
        self.mapping_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> Dict[str, str]:
        if not self.mapping_path.exists():
            return {}

        raw = self.mapping_path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}

        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Arquivo de mapeamento invalido: esperado objeto JSON")

        normalized: Dict[str, str] = {}
        for key, value in parsed.items():
            if isinstance(key, str) and isinstance(value, str):
                normalized[key] = value

        return normalized

    def _save(self, data: Dict[str, str]) -> None:
        self._ensure_parent()
        self.mapping_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def normalize_phone(phone: str) -> str:
        return "".join(ch for ch in phone if ch.isdigit() or ch == "+")

    def get_thread_id(self, user_phone_number: str) -> Optional[str]:
        normalized = self.normalize_phone(user_phone_number)
        if not normalized:
            return None
        data = self._load()
        return data.get(normalized)

    def set_mapping(self, user_phone_number: str, thread_id: str) -> str:
        normalized = self.normalize_phone(user_phone_number)
        normalized_thread_id = thread_id.strip()

        if not normalized:
            raise ValueError("Numero de telefone invalido")
        if not normalized_thread_id:
            raise ValueError("thread_id invalido")

        data = self._load()
        data[normalized] = normalized_thread_id
        self._save(data)
        return normalized

    def remove_mapping(self, user_phone_number: str) -> bool:
        normalized = self.normalize_phone(user_phone_number)
        if not normalized:
            return False

        data = self._load()
        if normalized not in data:
            return False

        data.pop(normalized, None)
        self._save(data)
        return True
