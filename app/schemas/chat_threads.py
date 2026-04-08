from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class DeleteThreadRequest(BaseModel):
    channel: str = Field(default="whatsapp", description="Canal de origem da thread")
    soft_delete: bool = Field(
        default=False,
        description="Se True, solicita exclusao logica no provedor quando suportado",
    )


class DeleteThreadResponse(BaseModel):
    thread_id: str
    deleted: bool
    channel: str
    provider_status_code: int
    message: str
    provider_response: Optional[Dict[str, Any]] = None
