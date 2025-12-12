# Build script for Windows - PowerShell
# Requires: Python 3.8+, pip, pyinstaller
Write-Host "Starting build..."
# Create venv optional
if (-Not (Test-Path .\venv)) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
# Build single-file exe; include the DB file next to exe
pyinstaller --onefile --add-data "compta.db;." --noconsole main.py
Write-Host "Build finished. Check the 'dist' folder for main.exe"
