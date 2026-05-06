from __future__ import annotations

from typing import Any, Dict, List

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSheetsService:
    def __init__(self, spreadsheet_id: str | None = None) -> None:
        self._client = self._build_client()
        self.spreadsheet_id = spreadsheet_id or settings.GOOGLE_SPREADSHEET_ID
        self._spreadsheet = self._client.open_by_key(self.spreadsheet_id)

    def _build_client(self) -> gspread.Client:
        credentials = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        return gspread.authorize(credentials)

    def get_worksheets(self) -> List[str]:
        return [worksheet.title for worksheet in self._spreadsheet.worksheets()]

    def get_sheet_values(self, sheet_name: str) -> Dict[str, Any]:
        """Retorna os dados da aba com headers e valores mapeados como dicionários."""
        worksheet = self._spreadsheet.worksheet(sheet_name)
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return {"headers": [], "rows": []}
        
        # Primeira linha são os headers
        headers = all_values[0]
        
        # Converter as linhas em dicionários
        rows = []
        for row in all_values[1:]:
            # Mapear cada valor ao seu header correspondente
            row_dict = {}
            for idx, header in enumerate(headers):
                # Usar valor vazio se a linha tiver menos colunas que headers
                row_dict[header] = row[idx] if idx < len(row) else ""
            rows.append(row_dict)
        
        return {
            "headers": headers,
            "rows": rows
        }

    def append_row(self, sheet_name: str, values: List[str]) -> dict:
        worksheet = self._spreadsheet.worksheet(sheet_name)
        result = worksheet.append_row(values=values, value_input_option="RAW")
        updates = result.get("updates", {}) if isinstance(result, dict) else {}
        return {
            "updated_range": updates.get("updatedRange"),
            "updated_rows": int(updates.get("updatedRows", 1)),
        }

    def get_spreadsheet_meta(self) -> dict:
        return {
            "spreadsheet_id": settings.GOOGLE_SPREADSHEET_ID,
            "title": self._spreadsheet.title,
            "worksheets": self.get_worksheets(),
        }
