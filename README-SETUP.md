# Configuração do Google Sheets API

## Problema Identificado

A API do Google Sheets às vezes funciona e às vezes não porque **o arquivo de credenciais não está configurado**. O sistema tenta usar autenticação primeiro, mas quando falha, faz fallback para acesso público.

## Como Resolver

### 1. Criar uma Service Account no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Sheets:
   - Vá para "APIs & Services" > "Library"
   - Procure por "Google Sheets API" e ative
4. Crie uma Service Account:
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "Service Account"
   - Preencha os detalhes e clique em "Create"
5. Gere uma chave JSON:
   - Na lista de service accounts, clique na que criou
   - Vá para "Keys" > "Add Key" > "Create new key"
   - Selecione "JSON" e baixe o arquivo

### 2. Configurar no Projeto

1. Renomeie o arquivo baixado para `credentials.json`
2. Coloque o arquivo em `backend/credentials/credentials.json`
3. Configure o ID da planilha no arquivo `.env`:
   ```
   GOOGLE_SPREADSHEET_ID=seu-spreadsheet-id-aqui
   ```

### 3. Compartilhar a Planilha com a Service Account

1. Abra sua planilha no Google Sheets
2. Clique em "Compartilhar"
3. Cole o email da service account (encontrado no arquivo JSON como `client_email`)
4. Dê permissões de "Editor" ou "Visualizador" conforme necessário

### 4. Testar a Configuração

Após configurar, reinicie o servidor e teste os endpoints:

```bash
# Verificar metadados
curl "http://localhost:8000/sheets/meta"

# Buscar dados de uma aba
curl "http://localhost:8000/sheets/worksheet?sheet_name=NomeDaAba"
```

## Logs de Diagnóstico

O sistema agora gera logs detalhados para ajudar no diagnóstico:

- `[WARNING] Arquivo de credenciais não encontrado` - Credenciais ausentes
- `[INFO] Cliente Google Sheets autenticado` - Autenticação OK
- `[INFO] Dados obtidos via autenticação` - Sucesso com credenciais
- `[INFO] Dados obtidos via acesso público` - Fallback funcionando

## Modos de Acesso

1. **Autenticado**: Usa credenciais para acessar planilhas privadas
2. **Público**: Fallback para planilhas compartilhadas publicamente
3. **Erro**: Quando ambos falham

## Troubleshooting

- **Erro 403**: Verifique se a service account tem acesso à planilha
- **Erro 404**: Planilha ou aba não encontrada
- **Timeout**: Planilha muito grande ou conexão lenta
- **Rate limiting**: Muitas requisições - aguarde alguns minutos