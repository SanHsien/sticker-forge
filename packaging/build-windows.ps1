$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repo

python -m pip install -e ".[dev,packaging]"
python -m pytest

$work = Join-Path $env:TEMP "sticker-forge-pyinstaller-build"
if (Test-Path $work) {
    Remove-Item -Recurse -Force $work
}

$dist = Join-Path $env:TEMP "sticker-forge-pyinstaller-dist"
if (Test-Path $dist) {
    Remove-Item -Recurse -Force $dist
}

python -m PyInstaller --clean --noconfirm packaging\sticker-forge.spec --distpath $dist --workpath $work
& (Join-Path $dist "sticker-forge\sticker-forge.exe") --help
Write-Host "Build output: $dist\sticker-forge"
