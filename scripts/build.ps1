param([string]$WixPath = "wix")
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name 'VidLift' --distpath dist --workpath build --specpath build src/vidlift.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
    & $WixPath build installer/Product.wxs -arch x64 -d "AppExe=$(Join-Path $repo 'dist\VidLift.exe')" -o dist/VidLift-1.1.0-x64.msi
    if ($LASTEXITCODE -ne 0) { throw 'MSI build failed' }
} finally { Pop-Location }
