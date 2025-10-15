# AURA RealtorProAI - Development Environment Setup Script
# Usage: pwsh automation/scripts/env.ps1

param()

$ErrorActionPreference = "Stop"

# Helper functions with ASCII-safe output
function Write-Info($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Write-Success($msg)    { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warning($msg)  { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Error($msg)   { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  AURA RealtorProAI Environment Setup" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

# Define paths
$RepoRoot = (Get-Location).Path
$Backend = Join-Path $RepoRoot "backend"
$Client = Join-Path $RepoRoot "aura-client"
$VenvDir = Join-Path $RepoRoot ".venv"
$BackendEnv = Join-Path $RepoRoot ".env"
$ClientEnv = Join-Path $Client ".env"

Write-Info "Repository root: $RepoRoot"
Write-Info "Backend path:    $Backend"
Write-Info "Client path:     $Client"
Write-Host ""

# Step 1: Check Prerequisites
Write-Host "Step 1: Checking Prerequisites" -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Success "Python found: $pythonVersion"
        # Basic version check (looking for 3.1x)
        if ($pythonVersion -match "Python 3\.1[1-9]|Python 3\.[2-9]") {
            Write-Success "Python version is compatible (3.11+)"
        } else {
            Write-Warning "Python version may be too old. 3.11+ recommended."
        }
    } else {
        throw "Python not found"
    }
} catch {
    Write-Error "Python 3.11+ is required but not found. Please install Python."
    Write-Info "Download from: https://www.python.org/downloads/"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Success "Node.js found: $nodeVersion"
        # Basic version check (looking for v18+)
        if ($nodeVersion -match "v1[8-9]\.|v[2-9][0-9]\.") {
            Write-Success "Node.js version is compatible (18+)"
        } else {
            Write-Warning "Node.js version may be too old. 18+ recommended."
        }
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Error "Node.js 18+ is required but not found. Please install Node.js."
    Write-Info "Download from: https://nodejs.org/"
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>$null
    if ($npmVersion) {
        Write-Success "npm found: v$npmVersion"
    } else {
        throw "npm not found"
    }
} catch {
    Write-Error "npm is required but not found. Usually comes with Node.js."
    exit 1
}

Write-Host ""

# Step 2: Setup Python Virtual Environment
Write-Host "Step 2: Setting up Python Virtual Environment" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow

if (Test-Path $VenvDir) {
    Write-Warning "Virtual environment already exists at .venv"
    Write-Info "Reusing existing virtual environment"
} else {
    Write-Info "Creating Python virtual environment..."
    try {
        python -m venv $VenvDir
        Write-Success "Virtual environment created at .venv"
    } catch {
        Write-Error "Failed to create virtual environment: $($_.Exception.Message)"
        exit 1
    }
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
try {
    & $ActivateScript
    Write-Success "Virtual environment activated"
} catch {
    Write-Error "Failed to activate virtual environment: $($_.Exception.Message)"
    exit 1
}

Write-Host ""

# Step 3: Install Backend Dependencies
Write-Host "Step 3: Installing Backend Dependencies" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

if (-not (Test-Path $Backend)) {
    Write-Error "Backend directory not found at: $Backend"
    Write-Info "Make sure you're running this script from the project root"
    exit 1
}

# Look for requirements file
$requirementsFile = $null
$possibleFiles = @("requirements.txt", "requirements-dev.txt", "pyproject.toml")

foreach ($file in $possibleFiles) {
    $fullPath = Join-Path $Backend $file
    if (Test-Path $fullPath) {
        $requirementsFile = $fullPath
        Write-Info "Found dependency file: $file"
        break
    }
}

if ($requirementsFile) {
    Write-Info "Installing Python dependencies..."
    try {
        pip install --upgrade pip
        if ($requirementsFile.EndsWith("pyproject.toml")) {
            pip install -e $Backend
        } else {
            pip install -r $requirementsFile
        }
        Write-Success "Backend dependencies installed successfully"
    } catch {
        Write-Error "Failed to install backend dependencies: $($_.Exception.Message)"
        Write-Info "Trying to install minimal dependencies..."
        try {
            pip install fastapi uvicorn google-generativeai python-dotenv sqlalchemy alembic
            Write-Warning "Installed minimal dependencies only"
        } catch {
            Write-Error "Failed to install even minimal dependencies"
            exit 1
        }
    }
} else {
    Write-Warning "No requirements file found. Installing minimal dependencies..."
    try {
        pip install --upgrade pip
        pip install fastapi uvicorn google-generativeai python-dotenv sqlalchemy alembic
        Write-Success "Minimal backend dependencies installed"
    } catch {
        Write-Error "Failed to install backend dependencies: $($_.Exception.Message)"
        exit 1
    }
}

Write-Host ""

# Step 4: Install Frontend Dependencies
Write-Host "Step 4: Installing Frontend Dependencies" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

if (-not (Test-Path $Client)) {
    Write-Error "Frontend directory not found at: $Client"
    Write-Info "Make sure the aura-client directory exists"
    exit 1
}

if (-not (Test-Path (Join-Path $Client "package.json"))) {
    Write-Error "package.json not found in frontend directory"
    exit 1
}

Write-Info "Installing frontend dependencies..."
try {
    Push-Location $Client
    npm install
    Pop-Location
    Write-Success "Frontend dependencies installed successfully"
} catch {
    Pop-Location
    Write-Error "Failed to install frontend dependencies: $($_.Exception.Message)"
    exit 1
}

Write-Host ""

# Step 5: Generate Environment Files
Write-Host "Step 5: Generating Environment Files" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Yellow

# Backend .env file
if (Test-Path $BackendEnv) {
    Write-Warning "Backend .env file already exists - skipping creation"
    Write-Info "Existing file: $BackendEnv"
} else {
    Write-Info "Creating backend .env file..."
    
    $backendEnvContent = "# AURA Backend Environment Configuration`n"
    $backendEnvContent += "# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    
    $backendEnvContent += "# AI Configuration`n"
    $backendEnvContent += "AI_PROVIDER=gemini`n"
    $backendEnvContent += "GEMINI_API_KEY=your-gemini-api-key-here`n"
    $backendEnvContent += "GEMINI_MODEL=gemini-1.5-pro`n"
    $backendEnvContent += "GEMINI_STT=true`n`n"
    
    $backendEnvContent += "# Database Configuration`n"
    $backendEnvContent += "DATABASE_URL=sqlite:///./aura_dev.db`n"
    $backendEnvContent += "# For PostgreSQL: postgresql+psycopg2://user:password@localhost:5432/aura`n`n"
    
    $backendEnvContent += "# Development Settings`n"
    $backendEnvContent += "DEBUG=true`n"
    $backendEnvContent += "ENVIRONMENT=development`n"
    $backendEnvContent += "DISABLE_AUTH=true`n`n"
    
    $backendEnvContent += "# API Configuration`n"
    $backendEnvContent += "CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:4173,http://localhost:5173`n"
    $backendEnvContent += "SECRET_KEY=dev-secret-key-change-in-production`n"
    $backendEnvContent += "ACCESS_TOKEN_EXPIRE_MINUTES=30`n`n"
    
    $backendEnvContent += "# Optional Services`n"
    $backendEnvContent += "# REDIS_URL=redis://localhost:6379`n"
    $backendEnvContent += "# CHROMADB_HOST=localhost`n"
    $backendEnvContent += "# CHROMADB_PORT=8000`n"
    
    try {
        $backendEnvContent | Out-File -FilePath $BackendEnv -Encoding UTF8
        Write-Success "Backend .env file created at: $BackendEnv"
    } catch {
        Write-Error "Failed to create backend .env file: $($_.Exception.Message)"
        exit 1
    }
}

# Frontend .env file
if (Test-Path $ClientEnv) {
    Write-Warning "Frontend .env file already exists - skipping creation"
    Write-Info "Existing file: $ClientEnv"
} else {
    Write-Info "Creating frontend .env file..."
    
    $frontendEnvContent = "# AURA Frontend Environment Configuration`n"
    $frontendEnvContent += "# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    
    $frontendEnvContent += "# API Configuration`n"
    $frontendEnvContent += "VITE_API_BASE_URL=http://localhost:8000`n"
    $frontendEnvContent += "VITE_API_VERSION=v1`n`n"
    
    $frontendEnvContent += "# Development Settings`n"
    $frontendEnvContent += "VITE_ENVIRONMENT=development`n"
    $frontendEnvContent += "VITE_DEBUG_MODE=true`n"
    $frontendEnvContent += "VITE_AURA_MOCK_MODE=true`n`n"
    
    $frontendEnvContent += "# Feature Flags`n"
    $frontendEnvContent += "VITE_ENABLE_VOICE_INPUT=true`n"
    $frontendEnvContent += "VITE_ENABLE_AI_SUGGESTIONS=true`n"
    $frontendEnvContent += "VITE_ENABLE_SSE=true`n"
    $frontendEnvContent += "VITE_ENABLE_DEBUG_LOGS=true`n"
    
    try {
        $frontendEnvContent | Out-File -FilePath $ClientEnv -Encoding UTF8
        Write-Success "Frontend .env file created at: $ClientEnv"
    } catch {
        Write-Error "Failed to create frontend .env file: $($_.Exception.Message)"
        exit 1
    }
}

Write-Host ""

# Step 6: Database Setup (Optional)
Write-Host "Step 6: Database Setup (Optional)" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

$alembicDir = Join-Path $Backend "alembic"
if (Test-Path $alembicDir) {
    Write-Info "Alembic migrations detected. Running database setup..."
    try {
        Push-Location $Backend
        alembic upgrade head
        Pop-Location
        Write-Success "Database migrations completed"
    } catch {
        Pop-Location
        Write-Warning "Database migration failed or not configured yet"
        Write-Info "This is normal if you haven't set up the database yet"
    }
} else {
    Write-Info "No Alembic migrations found - skipping database setup"
}

Write-Host ""

# Final Summary
Write-Host "================================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update your API keys in the .env files" -ForegroundColor White
Write-Host "   - Backend: $BackendEnv" -ForegroundColor Gray
Write-Host "   - Frontend: $ClientEnv" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Start the development servers:" -ForegroundColor White
Write-Host "   Backend:  cd backend && uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "   Frontend: cd aura-client && npm run dev" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Access the application:" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

Write-Host "4. For AI functionality, update GEMINI_API_KEY in .env" -ForegroundColor White
Write-Host ""

Write-Info "Environment setup completed successfully!"
Write-Host ""