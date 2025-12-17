# Bootstrap Development Environment for Windows
# This script sets up a Python virtual environment and installs development dependencies

Write-Host "Setting up development environment..." -ForegroundColor Green

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8 or later." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Cyan
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install development dependencies
if (Test-Path "requirements-dev.txt") {
    Write-Host "Installing development dependencies..." -ForegroundColor Yellow
    pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Some dependencies failed to install" -ForegroundColor Yellow
        Write-Host "This is okay - optional dependencies may fail on some systems" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: requirements-dev.txt not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment in the future, run:" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run Python tests:" -ForegroundColor Cyan
Write-Host "    pytest tests/" -ForegroundColor White
Write-Host ""
Write-Host "To build and test C++ code:" -ForegroundColor Cyan
Write-Host "    cd app" -ForegroundColor White
Write-Host "    mkdir build" -ForegroundColor White
Write-Host "    cd build" -ForegroundColor White
Write-Host "    cmake .." -ForegroundColor White
Write-Host "    cmake --build . --config Release" -ForegroundColor White
Write-Host "    ctest -C Release" -ForegroundColor White
Write-Host ""
