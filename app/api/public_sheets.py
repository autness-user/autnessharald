from fastapi import APIRouter, HTTPException, Query

from app.schemas.public_sheets import PublicSheetResponse
from app.services.public_sheets_service import PublicSheetsService

router = APIRouter()

# GIDs fixos das abas da planilha pública
_GID_PASCOA_RCA = "1432783051"
_GID_PASCOA_REG = "868986641"
_GID_CONSULTAR_VENDA_GRUPO_CLIENTE = "0"
_GID_ESTOQUE = "1374761486"


def _fetch(sheet_name: str, gid: str) -> PublicSheetResponse:
    try:
        headers, rows = PublicSheetsService().fetch_sheet(gid)
    except Exception as exc:
        error_msg = (
            f"Falha ao buscar dados da aba '{sheet_name}' (gid={gid}): {str(exc)}. "
            f"A planilha é pública (https://docs.google.com/spreadsheets/d/1oQpAdtb4HVLKAKZRIyj8CdrpHYh73FOcHZNuVtgBSSg). "
            f"Se testando via Swagger UI (no navegador), considere timeout longo (>30s). "
            f"Acesse a URL direto para melhor experiência: /public-sheets/{sheet_name.lower().replace(' ', '-')}"
        )
        raise HTTPException(
            status_code=502,
            detail=error_msg,
        ) from exc
    return PublicSheetResponse(
        sheet_name=sheet_name,
        gid=gid,
        total_rows=len(rows),
        headers=headers,
        rows=rows,
    )


@router.get(
    "/pascoa-rca",
    response_model=PublicSheetResponse,
    summary="Perfomance Páscoa RCA",
    description="Retorna todos os dados da aba 'Perfomance Páscoa RCA'.",
)
def pascoa_rca() -> PublicSheetResponse:
    return _fetch("Perfomance Páscoa RCA", _GID_PASCOA_RCA)


@router.get(
    "/pascoa-reg",
    response_model=PublicSheetResponse,
    summary="Perfomance Páscoa REG",
    description="Retorna todos os dados da aba 'Perfomance Páscoa REG'.",
)
def pascoa_reg() -> PublicSheetResponse:
    return _fetch("Perfomance Páscoa REG", _GID_PASCOA_REG)


@router.get(
    "/consultar-venda-grupo-cliente",
    response_model=PublicSheetResponse,
    summary="Consultar Venda Grupo Cliente",
    description="Retorna todos os dados da aba pública 'Consultar Venda Grupo Cliente' (gid=0). Se nenhum filtro for informado, retorna todos os registros. Filtros opcionais: 'Cod CLiente' (coluna B) e 'ID' (coluna D).",
)
def consultar_venda_grupo_cliente(
    cod_cliente: str | None = Query(
        None,
        alias="Cod CLiente",
        description="[OPCIONAL] Filtro pela coluna B ('Cod CLiente'). Se omitido, não filtra por cliente.",
    ),
    id_value: str | None = Query(
        None,
        alias="ID",
        description="[OPCIONAL] Filtro pela coluna D ('ID'). Se omitido, não filtra por ID.",
    ),
    limit: int | None = Query(
        None,
        ge=1,
        description="[OPCIONAL] Limita o número de registros retornados. Se omitido, retorna todos.",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="[OPCIONAL] Deslocamento para paginação. Padrão é 0 (começa do primeiro registro).",
    ),
) -> PublicSheetResponse:
    data = _fetch("Consultar Venda Grupo Cliente", _GID_CONSULTAR_VENDA_GRUPO_CLIENTE)

    if len(data.headers) < 4:
        raise HTTPException(
            status_code=500,
            detail="A aba 'Consultar Venda Grupo Cliente' não possui colunas suficientes para filtrar por 'Cod CLiente' e 'ID'.",
        )

    cod_cliente_column = data.headers[1]
    id_column = data.headers[3]
    filtered_rows = data.rows

    # Se nenhum filtro for informado, retorna todos os registros
    if cod_cliente is not None:
        cod_cliente_value = cod_cliente.strip().lower()
        filtered_rows = [
            row
            for row in filtered_rows
            if str(row.get(cod_cliente_column, "")).strip().lower() == cod_cliente_value
        ]

    if id_value is not None:
        id_value_normalized = id_value.strip().lower()
        filtered_rows = [
            row
            for row in filtered_rows
            if str(row.get(id_column, "")).strip().lower() == id_value_normalized
        ]

    # Aplicar paginação (offset e limit)
    paginated_rows = filtered_rows[offset:]
    if limit is not None:
        paginated_rows = paginated_rows[:limit]

    return PublicSheetResponse(
        sheet_name=data.sheet_name,
        gid=data.gid,
        total_rows=len(paginated_rows),
        headers=data.headers,
        rows=paginated_rows,
    )


@router.get(
    "/estoque",
    response_model=PublicSheetResponse,
    summary="Estoque",
    description="Retorna todos os dados da aba 'Estoque'.",
)
def estoque() -> PublicSheetResponse:
    return _fetch("Estoque", _GID_ESTOQUE)
