# Bootstraps the local Python environment and runs the GAL server.
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (!(Test-Path ".venv")) {
  py -3 -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if (-not $env:PORT) {
  $env:PORT = "5000"
}

python .\Backend\server.py
