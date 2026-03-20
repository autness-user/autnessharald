from fastapi import APIRouter, HTTPException, Query

from app.schemas.google_sheets import (
    AppendRowRequest,
    AppendRowResponse,
    SpreadsheetMetaResponse,
    WorksheetDataResponse,
)
from app.services.google_sheets_service import GoogleSheetsService

router = APIRouter()


def _service() -> GoogleSheetsService:
    try:
        return GoogleSheetsService()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao conectar no Google Sheets: {exc}") from exc


@router.get("/meta", response_model=SpreadsheetMetaResponse)
def spreadsheet_meta() -> SpreadsheetMetaResponse:
    meta = _service().get_spreadsheet_meta()
    return SpreadsheetMetaResponse(**meta)


@router.get("/worksheet", response_model=WorksheetDataResponse)
def worksheet_data(sheet_name: str = Query(..., description="Nome da aba")) -> WorksheetDataResponse:
    values = _service().get_sheet_values(sheet_name)
    return WorksheetDataResponse(sheet_name=sheet_name, rows=values)


@router.post("/append", response_model=AppendRowResponse)
def append_row(payload: AppendRowRequest) -> AppendRowResponse:
    result = _service().append_row(payload.sheet_name, payload.values)
    return AppendRowResponse(**result)
