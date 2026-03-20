from typing import Dict, List

from fastapi import APIRouter, HTTPException, Query

from app.schemas.performance import PerformanceSummaryResponse
from app.services.google_sheets_service import GoogleSheetsService

router = APIRouter()


@router.get("/summary", response_model=PerformanceSummaryResponse)
def performance_summary(sheet_name: str = Query(..., description="Nome da aba de performance")) -> PerformanceSummaryResponse:
    try:
        values = GoogleSheetsService().get_sheet_values(sheet_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao consultar performance: {exc}") from exc

    if not values:
        return PerformanceSummaryResponse(sheet_name=sheet_name, total_rows=0, headers=[], sample=[])

    headers = values[0]
    sample_rows = values[1:6]
    sample: List[Dict[str, str]] = []
    for row in sample_rows:
        row_dict = {headers[index]: row[index] if index < len(row) else "" for index in range(len(headers))}
        sample.append(row_dict)

    return PerformanceSummaryResponse(
        sheet_name=sheet_name,
        total_rows=max(len(values) - 1, 0),
        headers=headers,
        sample=sample,
    )
