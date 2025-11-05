# Deployment script for Student Attendance Tracker (PowerShell for Windows)
# This script helps deploy the application to production

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting deployment..." -ForegroundColor Green

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "❌ Please edit .env file and set SECRET_KEY before deploying!" -ForegroundColor Red
    Write-Host "Generate a secret key: python -c 'import secrets; print(secrets.token_hex(32))'" -ForegroundColor Yellow
    exit 1
}

# Check if SECRET_KEY is set and not default
$envContent = Get-Content .env -Raw
if ($envContent -match "change-this-secret-key-in-production" -or $envContent -match "your-secret-key-change-this") {
    Write-Host "❌ Please set a secure SECRET_KEY in .env file!" -ForegroundColor Red
    exit 1
}

# Create necessary directories
New-Item -ItemType Directory -Force -Path instance | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Deployment method selection
Write-Host ""
Write-Host "Select deployment method:"
Write-Host "1) Docker Compose (Recommended)"
Write-Host "2) Gunicorn (Direct)"
Write-Host "3) Docker (Standalone)"
$choice = Read-Host "Enter choice [1-3]"

switch ($choice) {
    "1" {
        Write-Host "📦 Deploying with Docker Compose..." -ForegroundColor Green
        
        # Build and start containers
        docker-compose down
        docker-compose build
        docker-compose up -d
        
        Write-Host "✅ Deployment complete!" -ForegroundColor Green
        Write-Host "Application is running at http://localhost:5000" -ForegroundColor Green
        Write-Host "View logs: docker-compose logs -f" -ForegroundColor Yellow
    }
    
    "2" {
        Write-Host "📦 Deploying with Gunicorn..." -ForegroundColor Green
        
        # Check if virtual environment exists
        if (-Not (Test-Path venv)) {
            Write-Host "Creating virtual environment..."
            python -m venv venv
        }
        
        # Activate virtual environment
        & .\venv\Scripts\Activate.ps1
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Initialize database
        python -c "from app import init_db; init_db()"
        
        # Start Gunicorn
        Write-Host "Starting Gunicorn server..." -ForegroundColor Green
        gunicorn -c gunicorn_config.py app:app
    }
    
    "3" {
        Write-Host "📦 Building Docker image..." -ForegroundColor Green
        
        # Build Docker image
        docker build -t student-tracker:latest .
        
        # Run container
        docker run -d `
            --name student_tracker `
            -p 5000:5000 `
            --env-file .env `
            -v ${PWD}/instance:/app/instance `
            -v ${PWD}/logs:/app/logs `
            --restart unless-stopped `
            student-tracker:latest
        
        Write-Host "✅ Deployment complete!" -ForegroundColor Green
        Write-Host "Application is running at http://localhost:5000" -ForegroundColor Green
        Write-Host "View logs: docker logs -f student_tracker" -ForegroundColor Yellow
    }
    
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Deployment successful!" -ForegroundColor Green

