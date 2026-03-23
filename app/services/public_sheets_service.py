from __future__ import annotations

import csv
import io
from typing import Dict, List, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SPREADSHEET_ID = "1oQpAdtb4HVLKAKZRIyj8CdrpHYh73FOcHZNuVtgBSSg"
REQUEST_TIMEOUT_SECONDS = 300

_EXPORT_URL = (
    "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export"
)

_GVIZ_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq"
)


class PublicSheetsService:
    """Acessa abas de uma planilha Google Sheets pública via exportação CSV."""

    def __init__(self, spreadsheet_id: str = SPREADSHEET_ID) -> None:
        self.spreadsheet_id = spreadsheet_id

        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session = requests.Session()
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def fetch_sheet(self, gid: str) -> Tuple[List[str], List[Dict[str, str]]]:
        """Busca os dados da aba identificada pelo gid.

        Returns:
            Tupla (headers, rows) onde rows é uma lista de dicts com os dados.
        """
        url = _EXPORT_URL.format(spreadsheet_id=self.spreadsheet_id)
        response = self._session.get(
            url,
            params={"format": "csv", "gid": gid},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        reader = csv.DictReader(io.StringIO(response.text))
        headers: List[str] = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = [dict(row) for row in reader]
        return headers, rows

    def fetch_sheet_values_by_name(self, sheet_name: str) -> List[List[str]]:
        """Busca os valores de uma aba pública pelo nome, sem credenciais.

        Retorna no mesmo formato usado por WorksheetDataResponse:
        [headers, row1, row2, ...]
        """
        url = _GVIZ_CSV_URL.format(spreadsheet_id=self.spreadsheet_id)
        response = self._session.get(
            url,
            params={"tqx": "out:csv", "sheet": sheet_name},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        reader = csv.reader(io.StringIO(response.text))
        return [row for row in reader]
