# start.ps1 - Bootstraps venv, installs deps, runs server
$ErrorActionPreference = "Stop"
$proj = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $proj

if (!(Test-Path .venv)) {
  py -3 -m venv .venv
}

# Activate venv
. .\.venv\Scripts\Activate.ps1

# Ensure PowerShell can run this script in this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null

# Install requirements
if (Test-Path .\requirements.txt) {
  pip install --disable-pip-version-check --quiet -r .\requirements.txt
} else {
  pip install --disable-pip-version-check --quiet flask flask-socketio eventlet
}

# Run the server
python .\server.py
