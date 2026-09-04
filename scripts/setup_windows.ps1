$ErrorActionPreference = "Stop"

Write-Host "Setting up Teddy AI for Windows..."

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3.9+ first."
}

if (-not (Test-Path "venv\Scripts\python.exe")) {
    py -m venv venv
}

$python = "venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Warning "FFmpeg is not installed. Install it with: winget install Gyan.FFmpeg"
} else {
    Write-Host "FFmpeg detected."
}

New-Item -ItemType Directory -Force -Path "models" | Out-Null
& $python -m piper.download_voices --data-dir models en_US-lessac-medium

Write-Host "Setup complete. Start Ollama separately, then run:"
Write-Host "  .\$python scripts\cli.py test all"
Write-Host "  .\$python scripts\cli.py demo --mode text"