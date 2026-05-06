from fastapi import APIRouter, HTTPException, Query

from app.schemas.google_sheets import (
    AppendRowRequest,
    AppendRowResponse,
    SpreadsheetMetaResponse,
    WorksheetDataResponse,
)
from app.services.google_sheets_service import GoogleSheetsService
from app.services.public_sheets_service import PublicSheetsService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


def _service() -> GoogleSheetsService:
    try:
        return GoogleSheetsService()
    except Exception as exc:
        logger.error(f"Falha ao conectar no Google Sheets: {exc}")
        raise HTTPException(status_code=500, detail=f"Falha ao conectar no Google Sheets: {exc}") from exc


@router.get("/meta", response_model=SpreadsheetMetaResponse)
def spreadsheet_meta() -> SpreadsheetMetaResponse:
    logger.info("Requisição para metadados da planilha")
    meta = _service().get_spreadsheet_meta()
    return SpreadsheetMetaResponse(**meta)


@router.get("/worksheet", response_model=WorksheetDataResponse)
def worksheet_data(sheet_name: str = Query(..., description="Nome da aba")) -> WorksheetDataResponse:
    logger.info(f"Requisição para dados da aba: {sheet_name}")

    try:
        data = _service().get_sheet_values(sheet_name)
        if data.get("rows"):
            logger.info(f"Dados retornados via autenticação: {len(data['rows'])} linhas")
            return WorksheetDataResponse(
                sheet_name=sheet_name,
                headers=data.get("headers", []),
                rows=data.get("rows", []),
                total_rows=len(data.get("rows", []))
            )
        else:
            logger.warning(f"Nenhum dado retornado via autenticação para aba '{sheet_name}', tentando fallback público")
    except HTTPException:
        logger.warning(f"Falha na autenticação, tentando fallback público para aba '{sheet_name}'")
    except Exception as e:
        logger.error(f"Erro inesperado na autenticação: {e}, tentando fallback público")

    try:
        logger.info(f"Tentando buscar aba '{sheet_name}' via acesso público")
        headers, rows = PublicSheetsService().fetch_sheet_by_name(sheet_name)
        logger.info(f"Dados retornados via acesso público: {len(rows)} linhas")
        return WorksheetDataResponse(
            sheet_name=sheet_name,
            headers=headers,
            rows=rows,
            total_rows=len(rows)
        )
    except Exception as exc:
        logger.error(f"Falha ao consultar aba pública '{sheet_name}': {exc}")
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao consultar aba '{sheet_name}': {exc}. Verifique se a aba existe e está pública.",
        ) from exc


@router.post("/append", response_model=AppendRowResponse)
def append_row(payload: AppendRowRequest) -> AppendRowResponse:
    logger.info(f"Requisição para adicionar linha na aba: {payload.sheet_name}")
    result = _service().append_row(payload.sheet_name, payload.values)
    return AppendRowResponse(**result)
