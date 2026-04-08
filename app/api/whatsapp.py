from fastapi import APIRouter, HTTPException

from app.schemas.whatsapp import (
    ErrorResponse,
    ResetThreadRequest,
    ResetThreadResponse,
    UpsertThreadMappingRequest,
    UpsertThreadMappingResponse,
)
from app.services.watsonx_threads_service import WatsonxThreadsService
from app.services.whatsapp_thread_mapping_service import WhatsAppThreadMappingService

router = APIRouter()


@router.post(
    "/thread-mapping",
    tags=["WhatsApp"],
    summary="Registra ou atualiza thread do usuario",
    description="Salva o vinculo numero do WhatsApp -> thread_id para uso no reset de conversa.",
    response_model=UpsertThreadMappingResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Requisicao invalida"},
        422: {"model": ErrorResponse, "description": "Erro de validacao dos campos enviados"},
        500: {"model": ErrorResponse, "description": "Erro interno ao salvar mapeamento"},
    },
    operation_id="upsertWhatsAppThreadMapping",
)
def upsert_whatsapp_thread_mapping(payload: UpsertThreadMappingRequest) -> UpsertThreadMappingResponse:
    service = WhatsAppThreadMappingService()

    try:
        normalized_phone = service.set_mapping(payload.user_phone_number, payload.thread_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": str(exc)},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Erro interno ao salvar mapeamento: {exc}"},
        ) from exc

    return UpsertThreadMappingResponse(
        status="success",
        user_phone_number=normalized_phone,
        thread_id=payload.thread_id.strip(),
        message="Mapeamento numero -> thread salvo com sucesso.",
    )


@router.post(
    "/reset-thread",
    tags=["WhatsApp"],
    summary="Reinicia a conversa do usuario no WhatsApp",
    description=(
        "Recebe o numero do usuario, localiza a thread atual associada e remove "
        "essa thread para que a proxima mensagem inicie uma nova conversa."
    ),
    response_model=ResetThreadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Requisicao invalida"},
        404: {"model": ErrorResponse, "description": "Nenhuma thread encontrada para o numero informado"},
        422: {"model": ErrorResponse, "description": "Erro de validacao dos campos enviados"},
        500: {"model": ErrorResponse, "description": "Erro interno ao tentar resetar a conversa"},
    },
    operation_id="resetWhatsAppThread",
)
def reset_whatsapp_thread(payload: ResetThreadRequest) -> ResetThreadResponse:
    mapping_service = WhatsAppThreadMappingService()
    normalized_phone = mapping_service.normalize_phone(payload.user_phone_number)

    if not normalized_phone:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Numero de telefone invalido."},
        )

    thread_id = mapping_service.get_thread_id(normalized_phone)
    if not thread_id:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Nenhuma thread encontrada para o numero informado.",
            },
        )

    try:
        status_code, provider_response = WatsonxThreadsService().delete_thread(
            thread_id=thread_id,
            channel="whatsapp",
            soft_delete=False,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Erro interno ao tentar resetar a conversa: {exc}"},
        ) from exc

    if status_code >= 400:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Falha ao remover thread no provedor de conversa.",
                "provider_response": provider_response,
            },
        )

    mapping_removed = False
    if payload.clear_mapping:
        mapping_removed = mapping_service.remove_mapping(normalized_phone)

    return ResetThreadResponse(
        status="success",
        user_phone_number=normalized_phone,
        thread_id_deleted=thread_id,
        mapping_removed=mapping_removed if payload.clear_mapping else None,
        message=(
            "Conversa reiniciada com sucesso. A proxima mensagem do usuario "
            "criara uma nova thread."
        ),
    )
