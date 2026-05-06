from __future__ import annotations

from typing import Any, Dict, List
import os

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSheetsService:
    def __init__(self, spreadsheet_id: str | None = None) -> None:
        self.spreadsheet_id = spreadsheet_id or settings.GOOGLE_SPREADSHEET_ID
        self._client = None
        self._spreadsheet = None
        self._build_client()

    def _build_client(self) -> None:
        """Constrói o cliente do Google Sheets com tratamento de erros."""
        try:
            if not os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
                logger.warning(f"Arquivo de credenciais não encontrado: {settings.GOOGLE_CREDENTIALS_PATH}")
                self._client = None
                return

            credentials = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
            self._client = gspread.authorize(credentials)
            logger.info("Cliente Google Sheets autenticado com sucesso")
        except Exception as e:
            logger.error(f"Falha na autenticação do Google Sheets: {e}")
            self._client = None

    def _ensure_spreadsheet(self):
        """Garante que a planilha está carregada."""
        if self._client and not self._spreadsheet:
            try:
                self._spreadsheet = self._client.open_by_key(self.spreadsheet_id)
                logger.info(f"Planilha carregada: {self._spreadsheet.title}")
            except Exception as e:
                logger.error(f"Falha ao abrir planilha {self.spreadsheet_id}: {e}")
                self._spreadsheet = None

    def get_worksheets(self) -> List[str]:
        """Retorna lista de abas da planilha."""
        if not self._client:
            logger.warning("Cliente não autenticado - retornando lista vazia")
            return []

        self._ensure_spreadsheet()
        if not self._spreadsheet:
            logger.error("Planilha não pôde ser carregada")
            return []

        try:
            worksheets = [worksheet.title for worksheet in self._spreadsheet.worksheets()]
            logger.info(f"Encontradas {len(worksheets)} abas: {worksheets}")
            return worksheets
        except Exception as e:
            logger.error(f"Erro ao listar abas: {e}")
            return []

    def get_sheet_values(self, sheet_name: str) -> Dict[str, Any]:
        """Retorna os dados da aba com headers e valores mapeados como dicionários."""
        if not self._client:
            logger.warning(f"Cliente não autenticado - não é possível buscar dados da aba '{sheet_name}'")
            return {"headers": [], "rows": []}

        self._ensure_spreadsheet()
        if not self._spreadsheet:
            logger.error(f"Planilha não pôde ser carregada - não é possível buscar aba '{sheet_name}'")
            return {"headers": [], "rows": []}

        try:
            worksheet = self._spreadsheet.worksheet(sheet_name)
            all_values = worksheet.get_all_values()
            logger.info(f"Aba '{sheet_name}' carregada com {len(all_values)} linhas brutas")

            if not all_values:
                logger.warning(f"Aba '{sheet_name}' está vazia")
                return {"headers": [], "rows": []}

            # Primeira linha são os headers
            headers = all_values[0]
            logger.info(f"Headers encontrados: {headers}")

            # Converter as linhas em dicionários
            rows = []
            for row_idx, row in enumerate(all_values[1:], 1):
                # Mapear cada valor ao seu header correspondente
                row_dict = {}
                for idx, header in enumerate(headers):
                    # Usar valor vazio se a linha tiver menos colunas que headers
                    row_dict[header] = row[idx] if idx < len(row) else ""
                rows.append(row_dict)

            logger.info(f"Processadas {len(rows)} linhas de dados da aba '{sheet_name}'")
            return {
                "headers": headers,
                "rows": rows
            }
        except Exception as e:
            logger.error(f"Erro ao buscar dados da aba '{sheet_name}': {e}")
            return {"headers": [], "rows": []}

    def append_row(self, sheet_name: str, values: List[str]) -> dict:
        """Adiciona uma linha à planilha."""
        if not self._client:
            raise Exception("Cliente não autenticado - não é possível adicionar linha")

        self._ensure_spreadsheet()
        if not self._spreadsheet:
            raise Exception("Planilha não pôde ser carregada")

        try:
            worksheet = self._spreadsheet.worksheet(sheet_name)
            result = worksheet.append_row(values=values, value_input_option="RAW")
            updates = result.get("updates", {}) if isinstance(result, dict) else {}
            logger.info(f"Linha adicionada à aba '{sheet_name}': {updates}")
            return {
                "updated_range": updates.get("updatedRange"),
                "updated_rows": int(updates.get("updatedRows", 1)),
            }
        except Exception as e:
            logger.error(f"Erro ao adicionar linha na aba '{sheet_name}': {e}")
            raise

    def get_spreadsheet_meta(self) -> dict:
        """Retorna metadados da planilha."""
        if not self._client:
            logger.warning("Cliente não autenticado - retornando metadados vazios")
            return {
                "spreadsheet_id": self.spreadsheet_id,
                "title": "Não autenticado",
                "worksheets": [],
            }

        self._ensure_spreadsheet()
        if not self._spreadsheet:
            logger.error("Planilha não pôde ser carregada")
            return {
                "spreadsheet_id": self.spreadsheet_id,
                "title": "Erro ao carregar",
                "worksheets": [],
            }

        try:
            meta = {
                "spreadsheet_id": self.spreadsheet_id,
                "title": self._spreadsheet.title,
                "worksheets": self.get_worksheets(),
            }
            logger.info(f"Metadados da planilha: {meta}")
            return meta
        except Exception as e:
            logger.error(f"Erro ao obter metadados: {e}")
            return {
                "spreadsheet_id": self.spreadsheet_id,
                "title": f"Erro: {e}",
                "worksheets": [],
            }
