from fastapi import APIRouter, HTTPException, Path

from app.schemas.chat_threads import DeleteThreadRequest, DeleteThreadResponse
from app.services.watsonx_threads_service import WatsonxThreadsService

router = APIRouter()


@router.delete(
    "/{thread_id}",
    response_model=DeleteThreadResponse,
    summary="Excluir thread de conversa",
    description="Exclui uma thread de conversa do canal WhatsApp (ou outro canal informado).",
)
def delete_thread(
    payload: DeleteThreadRequest,
    thread_id: str = Path(..., min_length=1, description="ID da thread para exclusao"),
) -> DeleteThreadResponse:
    try:
        status_code, provider_response = WatsonxThreadsService().delete_thread(
            thread_id=thread_id,
            channel=payload.channel,
            soft_delete=payload.soft_delete,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Falha ao autenticar no IAM antes de chamar o provedor",
                "thread_id": thread_id,
                "error": str(exc),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao excluir thread no watsonx: {exc}") from exc

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail={
                "message": "Erro retornado pelo provedor ao excluir a thread",
                "thread_id": thread_id,
                "provider_response": provider_response,
            },
        )

    return DeleteThreadResponse(
        thread_id=thread_id,
        deleted=True,
        channel=payload.channel,
        provider_status_code=status_code,
        message="Thread excluida com sucesso",
        provider_response=provider_response,
    )
