# Script de Atualização GitHub - init-github.ps1

## ✅ Status: Funcionando Perfeitamente

O script `init-github.ps1` foi completamente corrigido e melhorado com:

- ✅ **Sintaxe corrigida**: Resolvidos todos os erros de PowerShell
- ✅ **Mensagens coloridas**: Feedback visual claro durante execução
- ✅ **Tratamento robusto de erros**: Fallback HTTPS quando SSH falha
- ✅ **Sincronização inteligente**: Rebase automático com branch remoto
- ✅ **Filtro de segurança**: Remove automaticamente arquivos sensíveis do stage

## Como usar o script init-github.ps1

### Método 1: Execução direta (Recomendado)
```powershell
cd backend
.\init-github.ps1 -CommitMessage "Sua mensagem de commit"
```

### Método 2: Com PowerShell explícito
```powershell
cd backend
powershell -ExecutionPolicy Bypass -File .\init-github.ps1 -CommitMessage "Sua mensagem de commit"
```

### Método 3: Via comando do sistema
```cmd
cd backend
powershell -ExecutionPolicy Bypass -Command "& .\init-github.ps1 -CommitMessage 'Sua mensagem de commit'"
```

## Parâmetros disponíveis

- `-CommitMessage`: Mensagem do commit (obrigatório)
- `-RemoteUrl`: URL do repositório GitHub (opcional, padrão já configurado)
- `-Branch`: Nome do branch (opcional, padrão: main)
- `-GitPath`: Caminho para git.exe (opcional)

## Exemplo completo
```powershell
cd backend
.\init-github.ps1 -CommitMessage "Atualização das melhorias na API" -Branch "main"
```

## Funcionalidades

### 🔄 Sincronização Automática
- Detecta branch remoto existente
- Faz fetch e rebase automaticamente
- Evita conflitos de merge

### 🛡️ Segurança Integrada
- Remove automaticamente arquivos sensíveis:
  - `*.bak`, `*.tmp`, `*.key`
  - `credentials/*.json`
  - `.env*`
  - `ssh/code_engine_github`

### 🚀 Push Inteligente
- Tenta push via SSH primeiro
- Fallback automático para HTTPS se SSH falhar
- Mostra detalhes de erro quando necessário

### 📊 Feedback Visual
- Cores para indicar status das operações
- Emojis para identificação rápida
- Resumo final com detalhes do commit

## Troubleshooting

### Erro: "O termo 'init-github.ps1' não é reconhecido"
- **Solução**: Execute `cd backend` primeiro, depois `.\init-github.ps1`

### Erro: "ExecutionPolicy"
- **Solução**: Use `-ExecutionPolicy Bypass` ou execute como administrador

### Erro: "Não é possível carregar arquivo"
- **Solução**: Verifique se está no diretório correto (`backend/`)
- **Solução**: Execute `Unblock-File .\init-github.ps1` se necessário

### Erro: "Falha no push"
- **Verificação**: O script tenta automaticamente fallback para HTTPS
- **Verificação**: Verifique se as credenciais SSH estão configuradas corretamente

## Logs de Execução

O script fornece feedback detalhado:

```
=== Script de Publicacao GitHub ===
Diretorio atual: C:\path\to\backend
Script: C:\path\to\backend\init-github.ps1

Repositorio Git ja existe.
Criando commit com mensagem: 'Minha mensagem'
Commit criado com sucesso.
Atualizando remoto 'origin' para: https://github.com/user/repo.git
Branch remoto detectado, sincronizando com rebase...
Sincronizacao concluida.
Fazendo push para 'main'...
Push finalizado com sucesso!

Resumo:
   - Repositorio: https://github.com/user/repo.git
   - Branch: main
   - Commit: Minha mensagem
```

## Histórico de Correções

- **v1.1**: Corrigidos erros de sintaxe PowerShell
- **v1.0**: Mensagens coloridas e tratamento de erros aprimorado
- **v0.9**: Implementado fallback HTTPS para push
- **v0.8**: Adicionado filtro automático de arquivos sensíveis