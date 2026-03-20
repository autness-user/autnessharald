<#
.SYNOPSIS
Inicializa o repositório Git local e envia o backend para um repositório GitHub.

.DESCRIPTION
Este script:
  - Verifica se o Git está instalado
  - Inicializa um repositório (caso ainda não exista)
  - Faz commit dos arquivos do backend
  - Cria/atualiza o remoto `origin` para o URL informado
  - Faz push para o ramo principal (main por padrão)

.PARAMETER RemoteUrl
URL do repositório GitHub (ex: https://github.com/usuario/repo.git)

.PARAMETER Branch
Nome do ramo principal (padrão: main)
#>

param(
    [Parameter(Mandatory=$false, HelpMessage="URL do repositório GitHub (padrão: https://github.com/autness-user/autnessharald.git)")]
    [string]$RemoteUrl = 'https://github.com/autness-user/autnessharald.git',

    [Parameter(Mandatory=$false, HelpMessage="Nome do ramo principal. Padrão: main")]
    [string]$Branch = 'main',

    [Parameter(Mandatory=$false, HelpMessage="Caminho completo para git.exe (opcional)")]
    [string]$GitPath = ''
)

$Script:GitCmd = $null

function Find-Git {
    if ($GitPath -and (Test-Path $GitPath)) {
        return $GitPath
    }

    # Primeiro tenta usar o git do PATH
    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    # Em seguida tenta localizações padrão de instalação do Git no Windows
    $candidates = @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe",
        "C:\Program Files\Git\bin\git.exe",
        "C:\Program Files (x86)\Git\bin\git.exe"
    )

    foreach ($path in $candidates) {
        if (Test-Path $path) {
            return $path
        }
    }

    return $null
}

function Ensure-Git {
    $Script:GitCmd = Find-Git
    if (-not $Script:GitCmd) {
        Write-Error "Git não encontrado. Instale o Git (https://git-scm.com/) ou adicione ao PATH e execute novamente."
        exit 1
    }
}

function Ensure-GitRepo {
    if (-not (Test-Path .git)) {
        & $Script:GitCmd init
        Write-Host "Repositório Git inicializado."
    } else {
        Write-Host "Repositório Git já existe."
    }
}

# Garante que o script execute no diretório onde ele está
Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)

Ensure-Git
Ensure-GitRepo

# Adiciona arquivos e comita apenas se houver mudanças
$dirty = & $Script:GitCmd status --porcelain
if ($dirty) {
    & $Script:GitCmd add .
    & $Script:GitCmd commit -m "Initial commit" -q
    Write-Host "Commit criado."
} else {
    Write-Host "Nenhuma alteração a commitar."
}

# Define remote origin
$existing = & $Script:GitCmd remote | Where-Object { $_ -eq 'origin' }
if (-not $existing) {
    & $Script:GitCmd remote add origin $RemoteUrl
    Write-Host "Remoto 'origin' adicionado: $RemoteUrl"
} else {
    & $Script:GitCmd remote set-url origin $RemoteUrl
    Write-Host "Remoto 'origin' atualizado para: $RemoteUrl"
}

# Push
& $Script:GitCmd branch -M $Branch
Write-Host "Fazendo push para $Branch..."
& $Script:GitCmd push -u origin $Branch
Write-Host "Push finalizado."
