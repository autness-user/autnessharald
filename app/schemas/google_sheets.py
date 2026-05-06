from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class WorksheetDataResponse(BaseModel):
    sheet_name: str
    headers: List[str] = []
    rows: List[Dict[str, Any]] = []
    total_rows: int = 0


class AppendRowRequest(BaseModel):
    sheet_name: str
    values: List[str]


class AppendRowResponse(BaseModel):
    updated_range: Optional[str] = None
    updated_rows: int = 0


class SpreadsheetMetaResponse(BaseModel):
    spreadsheet_id: str
    title: str
    worksheets: List[str]
