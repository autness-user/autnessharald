# Backend - Google Sheets API

API FastAPI para leitura e escrita em planilhas Google Sheets.

## Como rodar localmente

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Documentação: `http://localhost:8000/docs`

## Variáveis de ambiente

Use o arquivo `.env` para configurar:

- `GOOGLE_SPREADSHEET_ID`
- `GOOGLE_CREDENTIALS_PATH`
- `HOST`
- `PORT`
- `DEBUG`
- `WATSONX_THREADS_API_BASE_URL`
- `WATSONX_THREADS_DELETE_PATH_TEMPLATE` (default: `/v1/threads/{thread_id}`)
- `WATSONX_BEARER_TOKEN` e/ou `WATSONX_API_KEY`
- `WATSONX_API_KEY_HEADER` (default: `x-api-key`)
- `WATSONX_PROJECT_ID` (opcional)
- `WATSONX_THREADS_TIMEOUT_SECONDS` (default: `30`)

## Endpoint para excluir thread de chat

`DELETE /chat-threads/{thread_id}`

Exemplo de payload:

```json
{
	"channel": "whatsapp",
	"soft_delete": false
}
```

Exemplo com cURL:

```bash
curl -X DELETE "http://localhost:8000/chat-threads/THREAD_ID_AQUI" \
	-H "Content-Type: application/json" \
	-d '{"channel":"whatsapp","soft_delete":false}'
```

## Docker

```bash
docker build -t autnessharald-backend .
docker run -p 8000:8000 autnessharald-backend
```
