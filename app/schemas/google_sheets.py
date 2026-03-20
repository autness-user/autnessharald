from typing import List, Optional

from pydantic import BaseModel


class WorksheetDataResponse(BaseModel):
    sheet_name: str
    rows: List[List[str]]


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
