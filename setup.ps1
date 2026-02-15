# Kaluwala CSR Libraries - Windows Setup Script
# Save this as setup.ps1 and run in PowerShell

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Kaluwala CSR Libraries Network Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create instance directory
Write-Host "`nCreating instance directory..." -ForegroundColor Yellow
if (-not (Test-Path "instance")) {
    New-Item -ItemType Directory -Path "instance" | Out-Null
}
Write-Host "✓ Instance directory ready" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nTo start the application:" -ForegroundColor Yellow
Write-Host "  python app.py" -ForegroundColor White
Write-Host "`nThen visit: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
