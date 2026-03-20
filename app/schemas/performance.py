from typing import Dict, List

from pydantic import BaseModel


class PerformanceSummaryResponse(BaseModel):
    sheet_name: str
    total_rows: int
    headers: List[str]
    sample: List[Dict[str, str]]
