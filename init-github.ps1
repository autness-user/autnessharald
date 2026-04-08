<#
.SYNOPSIS
Publica o backend no GitHub com commit limpo (sem backups/arquivos sensiveis).

.DESCRIPTION
Este script:
  - Verifica se o Git está instalado
  - Inicializa um repositório (caso ainda não exista)
  - Faz stage das mudanças
  - Remove do stage arquivos de backup/chaves sensiveis
  - Faz commit (se houver mudanças)
  - Cria/atualiza o remoto `origin`
  - Sincroniza com o remoto e faz push para o branch informado

.PARAMETER RemoteUrl
URL do repositório GitHub (ex: https://github.com/usuario/repo.git)

.PARAMETER Branch
Nome do branch principal (padrão: main)

.PARAMETER CommitMessage
Mensagem do commit

.PARAMETER GitPath
Caminho completo para git.exe (opcional)

.PARAMETER KeepCurrentBranch
Se informado, não força rename para o branch definido em -Branch.

.PARAMETER HttpsFallbackRemoteUrl
Remoto HTTPS usado como fallback quando o push SSH falhar por chave read-only.
#>

param(
    [Parameter(Mandatory = $false, HelpMessage = "URL do repositório GitHub (padrão: https://github.com/autness-user/autnessharald.git)")]
    [string]$RemoteUrl = 'https://github.com/autness-user/autnessharald.git',

    [Parameter(Mandatory = $false, HelpMessage = "Nome do branch principal. Padrão: main")]
    [string]$Branch = 'main',

    [Parameter(Mandatory = $false, HelpMessage = "Mensagem do commit. Padrão: Atualizacao do backend")]
    [string]$CommitMessage = 'Atualizacao do backend',

    [Parameter(Mandatory = $false, HelpMessage = "Caminho completo para git.exe (opcional)")]
    [string]$GitPath = '',

    [Parameter(Mandatory = $false, HelpMessage = "Nao renomeia branch atual para o valor de -Branch")]
    [switch]$KeepCurrentBranch,

    [Parameter(Mandatory = $false, HelpMessage = "Remoto HTTPS para fallback de push")]
    [string]$HttpsFallbackRemoteUrl = 'https://github.com/autness-user/autnessharald.git'
)

$ErrorActionPreference = 'Stop'
$Script:GitCmd = $null

function Fail([string]$Message) {
    Write-Error $Message
    exit 1
}

function Find-Git {
    if ($GitPath -and (Test-Path $GitPath)) {
        return $GitPath
    }

    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

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

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args,

        [Parameter(Mandatory = $false)]
        [string]$ErrorMessage = "Comando git falhou"
    )

    $hasNativePreference = $null -ne (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue)
    if ($hasNativePreference) {
        $previousNativePreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }

    try {
        $output = & $Script:GitCmd @Args 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        if ($hasNativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
    }

    if ($exitCode -ne 0) {
        if ($output) {
            Write-Host ($output -join [Environment]::NewLine)
        }
        Fail "$ErrorMessage (codigo $exitCode)."
    }

    return $output
}

function Invoke-GitCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $hasNativePreference = $null -ne (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue)
    if ($hasNativePreference) {
        $previousNativePreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }

    try {
        $output = & $Script:GitCmd @Args 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        if ($hasNativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
    }

    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output   = $output
    }
}

function Ensure-Git {
    $Script:GitCmd = Find-Git
    if (-not $Script:GitCmd) {
        Fail "Git nao encontrado. Instale o Git (https://git-scm.com/) ou informe -GitPath."
    }
}

function Ensure-GitRepo {
    if (-not (Test-Path .git)) {
        Invoke-Git -Args @('init') -ErrorMessage 'Falha ao inicializar repositorio Git'
        Write-Host "Repositorio Git inicializado."
    }
    else {
        Write-Host "Repositorio Git ja existe."
    }
}

function Exclude-UnsafeFromStage {
    $stagedFiles = & $Script:GitCmd diff --cached --name-only
    if ($LASTEXITCODE -ne 0) {
        Fail 'Falha ao listar arquivos staged para filtro de seguranca.'
    }

    if (-not $stagedFiles) {
        return
    }

    $unsafeRegex = @(
        '^ssh/.+\.bak.*$',
        '^ssh/.+\.tmp$',
        '^ssh/.+_backup.*$',
        '^.*\.bak$',
        '^.*\.tmp$',
        '^.*\.old$',
        '^.*\.orig$',
        '^.*\.swp$',
        '^.*\.key$',
        '^credentials/.+\.json$',
        '^\.env$',
        '^\.env\..+$',
        '^ssh/code_engine_github$'
    )

    foreach ($file in $stagedFiles) {
        $normalized = $file -replace '\\', '/'
        $isUnsafe = $false

        foreach ($pattern in $unsafeRegex) {
            if ($normalized -match $pattern) {
                $isUnsafe = $true
                break
            }
        }

        if ($isUnsafe) {
            $restoreRes = Invoke-GitCapture -Args @('restore', '--staged', '--', $normalized)
            if ($restoreRes.ExitCode -ne 0) {
                Fail "Falha ao remover arquivo inseguro do stage: $normalized"
            }
        }
    }
}

Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)

Ensure-Git
Ensure-GitRepo

Invoke-Git -Args @('add', '-A') -ErrorMessage 'Falha ao adicionar arquivos no stage'
Exclude-UnsafeFromStage

$staged = & $Script:GitCmd diff --cached --name-only
if ($LASTEXITCODE -ne 0) {
    Fail 'Falha ao verificar arquivos staged.'
}

if (-not $staged) {
    Write-Host 'Nenhuma alteracao valida para commit (apenas backups/sensiveis ou sem mudancas).'
}
else {
    Invoke-Git -Args @('commit', '-m', $CommitMessage) -ErrorMessage 'Falha ao criar commit'
    Write-Host 'Commit criado com sucesso.'
}

$existing = & $Script:GitCmd remote | Where-Object { $_ -eq 'origin' }
if ($LASTEXITCODE -ne 0) {
    Fail "Falha ao listar remotos Git."
}

if (-not $existing) {
    Invoke-Git -Args @('remote', 'add', 'origin', $RemoteUrl) -ErrorMessage "Falha ao adicionar remoto origin"
    Write-Host "Remoto 'origin' adicionado: $RemoteUrl"
}
else {
    Invoke-Git -Args @('remote', 'set-url', 'origin', $RemoteUrl) -ErrorMessage "Falha ao atualizar remoto origin"
    Write-Host "Remoto 'origin' atualizado para: $RemoteUrl"
}

if (-not $KeepCurrentBranch) {
    Invoke-Git -Args @('branch', '-M', $Branch) -ErrorMessage "Falha ao ajustar branch para $Branch"
}

$remoteExists = & $Script:GitCmd ls-remote --heads origin $Branch 2>$null
if ($LASTEXITCODE -eq 0 -and $remoteExists) {
    Write-Host "Branch remoto detectado, sincronizando com rebase..."
    Invoke-Git -Args @('fetch', 'origin', $Branch) -ErrorMessage 'Falha no fetch do remoto'
    Invoke-Git -Args @('pull', '--rebase', 'origin', $Branch) -ErrorMessage 'Falha no pull --rebase'
}

Write-Host "Fazendo push para $Branch..."
$pushAttempt = Invoke-GitCapture -Args @('push', '-u', 'origin', $Branch)

if ($pushAttempt.ExitCode -ne 0) {
    $pushText = ($pushAttempt.Output -join [Environment]::NewLine)
    $isSshReadOnly = $pushText -match 'read only' -or $pushText -match 'Could not read from remote repository'

    if ($isSshReadOnly -and $HttpsFallbackRemoteUrl) {
        Write-Host 'Push via SSH falhou com permissao read-only. Tentando fallback para HTTPS...'
        Invoke-Git -Args @('remote', 'set-url', 'origin', $HttpsFallbackRemoteUrl) -ErrorMessage 'Falha ao trocar remote para HTTPS'
        Invoke-Git -Args @('push', '-u', 'origin', $Branch) -ErrorMessage 'Falha no push via HTTPS'
    }
    else {
        if ($pushAttempt.Output) {
            Write-Host $pushText
        }
        Fail "Falha no push (codigo $($pushAttempt.ExitCode))."
    }
}

Write-Host 'Push finalizado com sucesso.'
