from typing import Dict, List

from pydantic import BaseModel


class PublicSheetResponse(BaseModel):
    sheet_name: str
    gid: str
    total_rows: int
    headers: List[str]
    rows: List[Dict[str, str]]
