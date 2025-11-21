# Setup script for AI Virtual Interview Coach
# Run this script to set up the environment

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI Virtual Interview Coach Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first install..." -ForegroundColor Gray

# Install core dependencies first
Write-Host "  Installing core packages..." -ForegroundColor Gray
pip install streamlit SpeechRecognition gTTS pyttsx3 textblob fpdf --quiet

# Install NLP packages
Write-Host "  Installing NLP packages (this may take longer)..." -ForegroundColor Gray
pip install sentence-transformers transformers torch --quiet --no-warn-script-location

# Install remaining packages
Write-Host "  Installing remaining packages..." -ForegroundColor Gray
pip install pandas numpy Pillow matplotlib plotly --quiet

Write-Host "All dependencies installed successfully!" -ForegroundColor Green

Write-Host ""

# Download NLTK data for TextBlob
Write-Host "Downloading TextBlob language data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('brown', quiet=True); nltk.download('punkt', quiet=True)"
Write-Host "Language data downloaded!" -ForegroundColor Green

Write-Host ""

# Create necessary directories
Write-Host "Creating project directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "reports" | Out-Null
Write-Host "Directories created!" -ForegroundColor Green

Write-Host ""

# Test imports
Write-Host "Testing imports..." -ForegroundColor Yellow
$testScript = @"
import streamlit
import speech_recognition
from gtts import gTTS
import textblob
from sentence_transformers import SentenceTransformer
print('All imports successful!')
"@

$testScript | python 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "All imports working correctly!" -ForegroundColor Green
} else {
    Write-Host "Warning: Some imports failed. This may not affect basic functionality." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Yellow
Write-Host "  streamlit run app_enhanced.py" -ForegroundColor White
Write-Host ""
Write-Host "Or run the simple version:" -ForegroundColor Yellow
Write-Host "  streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "For help, see:" -ForegroundColor Yellow
Write-Host "  - QUICKSTART.md for quick start guide" -ForegroundColor White
Write-Host "  - README.md for full documentation" -ForegroundColor White
Write-Host ""
Write-Host "Good luck with your interview practice! 🚀" -ForegroundColor Cyan
