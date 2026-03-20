from __future__ import annotations

from typing import List

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSheetsService:
    def __init__(self) -> None:
        self._client = self._build_client()
        self._spreadsheet = self._client.open_by_key(settings.GOOGLE_SPREADSHEET_ID)

    def _build_client(self) -> gspread.Client:
        credentials = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        return gspread.authorize(credentials)

    def get_worksheets(self) -> List[str]:
        return [worksheet.title for worksheet in self._spreadsheet.worksheets()]

    def get_sheet_values(self, sheet_name: str) -> List[List[str]]:
        worksheet = self._spreadsheet.worksheet(sheet_name)
        return worksheet.get_all_values()

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
