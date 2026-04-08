from typing import Optional

from pydantic import BaseModel, Field


class ResetThreadRequest(BaseModel):
    user_phone_number: str = Field(
        ...,
        description="Numero do usuario no formato E.164",
        examples=["+5511999999999"],
    )
    clear_mapping: bool = Field(
        default=True,
        description="Remove o vinculo numero -> thread_id do storage interno",
    )


class ResetThreadResponse(BaseModel):
    status: str = Field(default="success", examples=["success"])
    user_phone_number: str
    thread_id_deleted: Optional[str] = Field(default=None, examples=["th_abc123"])
    mapping_removed: Optional[bool] = Field(default=None, examples=[True])
    message: str


class UpsertThreadMappingRequest(BaseModel):
    user_phone_number: str = Field(
        ...,
        description="Numero do usuario no formato E.164",
        examples=["+5511999999999"],
    )
    thread_id: str = Field(
        ...,
        min_length=1,
        description="ID da thread atual do usuario",
        examples=["th_abc123"],
    )


class UpsertThreadMappingResponse(BaseModel):
    status: str = Field(default="success", examples=["success"])
    user_phone_number: str
    thread_id: str
    message: str


class ErrorResponse(BaseModel):
    status: str = Field(default="error", examples=["error"])
    message: str
