# Script de Atualização GitHub

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

## Troubleshooting

### Erro: "O termo 'init-github.ps1' não é reconhecido"
- **Solução**: Execute `cd backend` primeiro, depois `.\init-github.ps1`

### Erro: "ExecutionPolicy"
- **Solução**: Use `-ExecutionPolicy Bypass` ou execute como administrador

### Erro: "Não é possível carregar arquivo"
- **Solução**: Verifique se está no diretório correto (`backend/`)
- **Solução**: Execute `Unblock-File .\init-github.ps1` se necessário