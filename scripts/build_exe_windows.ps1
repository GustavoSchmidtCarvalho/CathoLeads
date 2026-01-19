param(
  [ValidateSet('onedir','onefile')]
  [string]$Mode = 'onedir',
  [ValidateSet('chromium','firefox','webkit','all')]
  [string]$Browser = 'chromium'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "==> Instalando dependências" -ForegroundColor Cyan
python -m pip install -r requirements.txt
python -m pip install pyinstaller

Write-Host "==> Instalando browser do Playwright ($Browser)" -ForegroundColor Cyan
if ($Browser -eq 'all') {
  python -m playwright install
} else {
  python -m playwright install $Browser
}

Write-Host "==> Build do executável (PyInstaller: $Mode)" -ForegroundColor Cyan
$pyiArgs = @(
  '--noconfirm',
  '--clean',
  '--name', 'CathoLeads',
  '--console'
)

if ($Mode -eq 'onefile') {
  $pyiArgs += '--onefile'
} else {
  $pyiArgs += '--onedir'
}

# Ajuda o PyInstaller a coletar recursos de libs comuns
$pyiArgs += @('--collect-all', 'playwright')
$pyiArgs += @('--collect-all', 'pandas')
$pyiArgs += @('--collect-all', 'openpyxl')

$pyiArgs += 'src\\catho_leads.py'

python -m PyInstaller @pyiArgs

$distApp = Join-Path $repoRoot 'dist\\CathoLeads'

Write-Host "==> Copiando config e pastas de saída" -ForegroundColor Cyan
New-Item -ItemType Directory -Force (Join-Path $distApp 'config') | Out-Null
Copy-Item -Force (Join-Path $repoRoot 'config\\config.example.json') (Join-Path $distApp 'config\\config.example.json')

# Atalho clicável para rodar o exe e abrir o log ao final
Copy-Item -Force (Join-Path $repoRoot 'scripts\\run_catholeads.bat') (Join-Path $distApp 'run_catholeads.bat')

# Cria um config.json inicial para facilitar (usuário edita depois)
if (-not (Test-Path (Join-Path $distApp 'config\\config.json'))) {
  Copy-Item -Force (Join-Path $repoRoot 'config\\config.example.json') (Join-Path $distApp 'config\\config.json')
}

New-Item -ItemType Directory -Force (Join-Path $distApp 'output\\candidates\\json') | Out-Null
New-Item -ItemType Directory -Force (Join-Path $distApp 'output\\candidates\\csv') | Out-Null
New-Item -ItemType Directory -Force (Join-Path $distApp 'output\\candidates\\excel') | Out-Null
New-Item -ItemType Directory -Force (Join-Path $distApp 'output\\screenshots') | Out-Null
New-Item -ItemType Directory -Force (Join-Path $distApp 'output\\logs') | Out-Null

# Empacotar browsers do Playwright junto (para rodar sem Python no PC alvo)
$msPlaywright = Join-Path $env:LOCALAPPDATA 'ms-playwright'
if (Test-Path $msPlaywright) {
  Write-Host "==> Empacotando browsers do Playwright" -ForegroundColor Cyan
  Copy-Item -Recurse -Force $msPlaywright (Join-Path $distApp 'ms-playwright')
} else {
  Write-Warning "Pasta de browsers do Playwright não encontrada em $msPlaywright. O exe pode falhar ao abrir o browser."
}

Write-Host "\nBuild pronto em: $distApp" -ForegroundColor Green
Write-Host "Abra 'config\\config.json' dentro do dist e preencha suas credenciais." -ForegroundColor Green
