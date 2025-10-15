# AURA RealtorProAI - Environment Setup Script
param()

$ErrorActionPreference = "Stop"

function Write-Info($msg)  { Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "❌ $msg" -ForegroundColor Red }

# Paths
$RepoRoot   = (Get-Location).Path
$Backend    = Join-Path $RepoRoot "backend"
$Client     = Join-Path $RepoRoot "aura-client"
$VenvDir    = Join-Path $RepoRoot ".venv"
$BackendEnv = Join-Path $RepoRoot ".env"
$ClientEnv  = Join-Path $Client ".env"

Write-Info "Repository root: $RepoRoot"
Write-Info "Backend path:    $Backend"
Write-Info "Client path:     $Client"

# Prerequisites check
Write-Info "Checking prerequisites..."

try {
  $pyv = python --version 2>$null
  if (-not $pyv) { throw "Python not found" }
  Write-Ok "Python detected: $pyv"
} catch {
  Write-Err "Python 3.11+ is required. Install Python and re-run."
  exit 1
}

try {
  $nodev = node --version 2>$null
  if (-not $nodev) { throw "Node not found" }
  Write-Ok "Node detected: $nodev"
} catch {
  Write-Err "Node 18+ is required. Install Node and re-run."
  exit 1
}

try {
  $npmd = npm --version 2>$null
  if (-not $npmd) { throw "npm not found" }
  Write-Ok "npm detected: v$npmd"
} catch {
  Write-Err "npm is required. Install Node/npm and re-run."
  exit 1
}

# Python virtualenv
if (Test-Path $VenvDir) {
  Write-Warn "Existing virtualenv found at .venv - reusing."
} else {
  Write-Info "Creating virtualenv at .venv..."
  python -m venv $VenvDir
  Write-Ok "Virtualenv created."
}

# Activate virtualenv
$Activate = Join-Path $VenvDir "Scripts\Activate.ps1"
& $Activate
Write-Ok "Virtualenv activated."

# Backend dependencies
if (-not (Test-Path $Backend)) { 
  Write-Err "Backend folder not found at $Backend"
  exit 1 
}

Write-Info "Installing backend dependencies..."
$reqFile = @("requirements.txt","requirements-dev.txt","pyproject.toml") | 
  ForEach-Object { Join-Path $Backend $_ } | 
  Where-Object { Test-Path $_ } | 
  Select-Object -First 1

if ($null -eq $reqFile) {
  Write-Warn "No standard Python dependency file found. Installing minimal AI libs."
  pip install --upgrade pip
  pip install fastapi uvicorn google-generativeai google-cloud-aiplatform python-dotenv
} else {
  pip install --upgrade pip
  if ($reqFile.EndsWith("pyproject.toml")) {
    pip install -e $Backend
  } else {
    pip install -r $reqFile
  }
}
Write-Ok "Backend dependencies installed."

# Frontend dependencies
if (-not (Test-Path $Client)) { 
  Write-Err "Client folder not found at $Client"
  exit 1 
}

Write-Info "Installing frontend dependencies..."
Push-Location $Client
npm install
Pop-Location
Write-Ok "Frontend dependencies installed."

# Environment configuration
Write-Info "Collecting environment configuration..."

if (-not (Test-Path $BackendEnv)) {
  $GEMINI = Read-Host "Enter GEMINI_API_KEY (required)"
  if ([string]::IsNullOrWhiteSpace($GEMINI)) {
    Write-Err "GEMINI_API_KEY is required to proceed."
    exit 1
  }
  $PROJECT = Read-Host "Enter VERTEX_PROJECT_ID (optional, press Enter to skip)"
  $LOCATION = Read-Host "Enter VERTEX_LOCATION (default: us-central1)"
  if ([string]::IsNullOrWhiteSpace($LOCATION)) { $LOCATION = "us-central1" }

  $backendEnvContent = @"
# AURA Backend .env
AI_PROVIDER=gemini
GEMINI_API_KEY=$GEMINI
GEMINI_MODEL=gemini-1.5-pro
GEMINI_STT=true
VERTEX_PROJECT_ID=$PROJECT
VERTEX_LOCATION=$LOCATION

# Database (override as needed)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/aura

# CORS / API
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:4173
"@

  $backendEnvContent | Out-File -Encoding UTF8 $BackendEnv
  Write-Ok "Created backend .env"
} else {
  Write-Warn ".env already exists at repo root - leaving as-is."
}

if (-not (Test-Path $ClientEnv)) {
  $clientEnvContent = @"
# AURA Client .env
VITE_API_BASE_URL=http://localhost:8000
VITE_AURA_MOCK_MODE=false
VITE_ENABLE_SSE=true
VITE_ENABLE_DEBUG_LOGS=true
"@

  $clientEnvContent | Out-File -Encoding UTF8 $ClientEnv
  Write-Ok "Created client .env"
} else {
  Write-Warn "aura-client/.env already exists - leaving as-is."
}

# Database migration check
$AlembicIni = Join-Path $RepoRoot "alembic.ini"
if (Test-Path $AlembicIni -or (Test-Path (Join-Path $Backend "alembic"))) {
  Write-Info "Running Alembic migrations (if configured)..."
  try {
    Push-Location $Backend
    if (Test-Path "alembic.ini") {
      alembic upgrade head
    } else {
      Write-Warn "No alembic.ini found in backend; skipping migrations."
    }
    Pop-Location
    Write-Ok "Database migration step finished."
  } catch {
    Write-Warn "Alembic migration failed or not configured. Continue if DB is not required yet."
  }
} else {
  Write-Warn "Alembic not detected - skipping DB migration."
}

# Final messages
Write-Ok "Setup complete."
Write-Info "Run servers:"
Write-Host "  # Backend" -ForegroundColor Magenta
Write-Host "  cd $Backend && uvicorn app.main:app --reload"
Write-Host "  # Frontend" -ForegroundColor Magenta  
Write-Host "  cd $Client && npm run dev"

Write-Info "Quick smoke tests:"
Write-Host "  Invoke-WebRequest http://localhost:8000/docs -UseBasicParsing"
Write-Host "  curl http://localhost:8000/api/v1/intelligence/health"