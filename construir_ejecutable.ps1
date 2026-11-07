$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

python -m PyInstaller --version *> $null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller no está instalado. Ejecute: python -m pip install -r requirements-build.txt"
}

$specPath = Join-Path $PSScriptRoot "build\pyinstaller"
New-Item -ItemType Directory -Path $specPath -Force | Out-Null
$ejecutableActual = Join-Path $PSScriptRoot "DatosDemoCL.exe"
if (Test-Path -LiteralPath $ejecutableActual) {
    $carpetaVersiones = Join-Path $specPath "versiones-anteriores"
    New-Item -ItemType Directory -Path $carpetaVersiones -Force | Out-Null
    $marcaTiempo = Get-Date -Format "yyyyMMdd-HHmmss"
    $respaldo = Join-Path $carpetaVersiones "DatosDemoCL-$marcaTiempo.exe"
    Move-Item -LiteralPath $ejecutableActual -Destination $respaldo
}

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name DatosDemoCL `
    --distpath $PSScriptRoot `
    --workpath (Join-Path $specPath "work") `
    --specpath $specPath `
    --paths $PSScriptRoot `
    (Join-Path $PSScriptRoot "datosdemocl_app.py")

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller no pudo construir DatosDemoCL.exe."
}

Write-Host "Ejecutable listo: $(Join-Path $PSScriptRoot 'DatosDemoCL.exe')"
