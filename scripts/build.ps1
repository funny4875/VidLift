param([string]$WixPath = "wix")
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name '簡報影片匯出工具' --distpath dist --workpath build --specpath build src/pptx_video_extractor.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
    & $WixPath build installer/Product.wxs -arch x64 -d "AppExe=$(Join-Path $repo 'dist\簡報影片匯出工具.exe')" -o dist/PptxVideoExtractor-1.0.0-x64.msi
    if ($LASTEXITCODE -ne 0) { throw 'MSI build failed' }
} finally { Pop-Location }
