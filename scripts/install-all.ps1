$ErrorActionPreference = "Stop"

Write-Host "Installing backend Python dependencies..."
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Installing frontend npm dependencies..."
Push-Location frontend
npm install
Pop-Location

Write-Host "Install completed."
