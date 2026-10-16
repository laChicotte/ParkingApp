param([switch]$Installer, [string]$InnoCompiler)
$ErrorActionPreference = 'Stop'
$projectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $projectDir '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Creer .venv et installer requirements-build.txt avant la compilation.' }
Push-Location $projectDir
try {
    & $python -c "from PIL import Image; from pathlib import Path; Path('build').mkdir(exist_ok=True); Image.open('logo.png').save('build/ukag.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
    if ($LASTEXITCODE -ne 0) { throw 'La preparation du logo a echoue.' }
    & $python -m PyInstaller --noconfirm parking.spec
    if ($LASTEXITCODE -ne 0) { throw 'La compilation PyInstaller a echoue.' }
    if ($Installer) {
        if (-not $InnoCompiler) {
            $candidates = @(
                (Join-Path $projectDir 'build\installer-tools\InnoSetup\ISCC.exe'),
                'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
                'C:\Program Files\Inno Setup 6\ISCC.exe'
            )
            $InnoCompiler = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        }
        if (-not $InnoCompiler) { throw 'Compilateur Inno Setup introuvable. Utiliser -InnoCompiler avec le chemin de ISCC.exe.' }
        & $InnoCompiler (Join-Path $projectDir 'installer\UKAGParking.iss')
        if ($LASTEXITCODE -ne 0) { throw 'La creation de l installateur a echoue.' }
    }
} finally {
    Pop-Location
}
