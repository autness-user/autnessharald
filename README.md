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

## Docker

```bash
docker build -t autnessharald-backend .
docker run -p 8000:8000 autnessharald-backend
```
