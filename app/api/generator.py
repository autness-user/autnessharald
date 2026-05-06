import re
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Query

from app.services.google_sheets_service import GoogleSheetsService
from app.services.public_sheets_service import PublicSheetsService

router = APIRouter()


def _validate_google_sheets_url(url: str) -> str:
    """Valida URL do Google Sheets e extrai o ID da planilha."""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        raise HTTPException(
            status_code=400,
            detail="URL inválida. Use um link do Google Sheets válido (https://docs.google.com/spreadsheets/d/...)"
        )
    return match.group(1)


def _build_sheet_schema(headers: List[str], sample_row: dict[str, Any]) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}
    for idx, header in enumerate(headers):
        key = header.strip() or f"column_{idx + 1}"
        properties[key] = {
            "type": "string",
            "title": header or key,
            "description": f"Valor da coluna '{header or key}'",
        }
        if sample_row.get(header, sample_row.get(key)) is not None:
            properties[key]["example"] = sample_row.get(header, sample_row.get(key), "")
    return {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "description": "Linha de dados da planilha com campos nomeados",
        "example": sample_row,
    }


def _build_sheet_example(headers: List[str], rows: List[dict[str, Any]]) -> dict[str, Any]:
    sample_rows: List[dict[str, Any]] = []
    if rows:
        sample_rows.append(rows[0])
    return {
        "sheet_name": "",
        "headers": headers,
        "rows": sample_rows,
        "total_rows": len(rows),
    }


def _fetch_sheet_data(spreadsheet_id: str, sheet_name: str) -> Dict[str, Any]:
    """Busca dados da planilha, tentando primeiro autenticação e depois fallback público."""
    from app.utils.logger import get_logger
    logger = get_logger(__name__)

    try:
        logger.info(f"Tentando buscar dados via autenticação para planilha {spreadsheet_id}, aba '{sheet_name}'")
        service = GoogleSheetsService(spreadsheet_id=spreadsheet_id)
        data = service.get_sheet_values(sheet_name)
        if data.get("rows"):
            logger.info(f"Dados obtidos via autenticação: {len(data['rows'])} linhas")
            return data
        else:
            logger.warning(f"Nenhum dado retornado via autenticação, tentando fallback público")
    except Exception as e:
        logger.warning(f"Falha na autenticação ({e}), tentando fallback público para planilha {spreadsheet_id}")

    try:
        logger.info(f"Buscando dados via acesso público para aba '{sheet_name}'")
        headers, rows = PublicSheetsService(spreadsheet_id=spreadsheet_id).fetch_sheet_by_name(sheet_name)
        logger.info(f"Dados obtidos via acesso público: {len(rows)} linhas")
        return {"headers": headers, "rows": rows}
    except Exception as e:
        logger.error(f"Falha em ambos os métodos de acesso para aba '{sheet_name}': {e}")
        # Retorna dados vazios em vez de falhar
        return {"headers": [], "rows": []}


def _generate_openapi_spec(
    spreadsheet_url: str,
    spreadsheet_id: str,
    base_url: str,
    sheet_name: str = "Perfomance Pascoa RCA"
) -> Dict[str, Any]:
    """Gera especificação OpenAPI completa para a planilha Google Sheets."""
    sheet_data = _fetch_sheet_data(spreadsheet_id, sheet_name)
    headers = sheet_data.get("headers", [])
    rows = sheet_data.get("rows", [])
    sample_row = rows[0] if rows else {header: "" for header in headers}
    row_schema = _build_sheet_schema(headers, sample_row)
    response_example = _build_sheet_example(headers, rows)

    return {
        "openapi": "3.0.1",
        "info": {
            "title": f"Google Sheets API - {spreadsheet_id}",
            "version": "1.0.0",
            "description": f"API gerada automaticamente para a planilha Google Sheets: {spreadsheet_url}",
            "contact": {
                "name": "Autness IA",
                "url": "https://autness.com.br"
            }
        },
        "servers": [
            {
                "url": base_url,
                "description": "Servidor de API da planilha"
            }
        ],
        "paths": {
            "/sheets/worksheet": {
                "get": {
                    "tags": ["Sheets"],
                    "summary": "Obter dados da planilha",
                    "description": f"Retorna os dados de uma aba da planilha Google Sheets especificada",
                    "operationId": "get_worksheet_data",
                    "parameters": [
                        {
                            "name": "sheet_name",
                            "in": "query",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "description": "Nome da aba da planilha",
                                "default": sheet_name
                            },
                            "description": "Nome da aba da planilha",
                            "example": sheet_name
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Dados da planilha retornados com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/WorksheetDataResponse"
                                    },
                                    "examples": {
                                        "worksheetExample": {
                                            "summary": "Exemplo de retorno da planilha",
                                            "value": response_example
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Requisição inválida",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        },
                        "502": {
                            "description": "Erro ao consultar a planilha",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "WorksheetDataResponse": {
                    "type": "object",
                    "title": "WorksheetDataResponse",
                    "description": "Resposta contendo dados de uma aba da planilha",
                    "properties": {
                        "sheet_name": {
                            "type": "string",
                            "title": "Sheet Name",
                            "description": "Nome da aba da planilha"
                        },
                        "headers": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "title": "Headers",
                            "description": "Nomes das colunas da planilha"
                        },
                        "rows": {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/WorksheetRow"
                            },
                            "title": "Rows",
                            "description": "Dados da planilha com colunas nomeadas"
                        },
                        "total_rows": {
                            "type": "integer",
                            "title": "Total Rows",
                            "description": "Quantidade total de linhas de dados"
                        }
                    },
                    "required": ["sheet_name", "headers", "rows", "total_rows"],
                    "example": response_example
                },
                "WorksheetRow": row_schema,
                "ErrorResponse": {
                    "type": "object",
                    "title": "ErrorResponse",
                    "description": "Resposta de erro",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Descrição do erro"
                        }
                    },
                    "required": ["detail"]
                }
            }
        }
    }


@router.get("/generate-api", response_model=Dict[str, Any])
def generate_api_specification(
    sheet_url: str = Query(..., description="Link completo da planilha Google Sheets"),
    base_url: str = Query(
        default="http://localhost:8000",
        description="URL base da API (ex: http://localhost:8000 ou https://api.exemplo.com)"
    ),
    sheet_name: str = Query(
        default="Perfomance Pascoa RCA",
        description="Nome padrão da aba para incluir na especificação (opcional)"
    )
) -> Dict[str, Any]:
    """
    Gera uma especificação OpenAPI completa para uma planilha Google Sheets.
    
    A especificação gerada pode ser importada diretamente no IBM Watson Orchestrate
    e em outras ferramentas que suportam OpenAPI 3.0.1.
    
    Args:
        sheet_url: Link da planilha (ex: https://docs.google.com/spreadsheets/d/1Jgl.../edit)
        base_url: URL base onde a API está hospedada
        sheet_name: Nome da aba padrão a incluir na especificação
    
    Returns:
        Especificação OpenAPI 3.0.1 em formato JSON
    """
    # Validar e extrair ID da planilha
    spreadsheet_id = _validate_google_sheets_url(sheet_url)
    
    # Gerar especificação
    spec = _generate_openapi_spec(
        spreadsheet_url=sheet_url,
        spreadsheet_id=spreadsheet_id,
        base_url=base_url,
        sheet_name=sheet_name
    )
    
    return {
        "success": True,
        "spreadsheet_id": spreadsheet_id,
        "specification": spec
    }


@router.post("/validate-sheet-url")
def validate_sheet_url(sheet_url: str = Query(..., description="URL da planilha Google Sheets")) -> Dict[str, Any]:
    """
    Valida uma URL de planilha Google Sheets e extrai o ID.
    
    Args:
        sheet_url: URL completa da planilha
    
    Returns:
        Informações extraídas da URL
    """
    spreadsheet_id = _validate_google_sheets_url(sheet_url)
    
    return {
        "valid": True,
        "spreadsheet_id": spreadsheet_id,
        "message": "URL valida e pronta para gerar especificacao OpenAPI"
    }
