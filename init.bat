@echo off
REM ============================================================================
REM RHIZ PROJECT INITIALIZATION SCRIPT
REM First-time setup for Rhiz_LocalDev environment
REM Windows batch script for Dell Inspiron 15 3535
REM ============================================================================

echo.
echo ========================================
echo RHIZ PROJECT INITIALIZATION
echo ========================================
echo.

REM Check if running as Administrator (recommended for Docker)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator.
    echo Some Docker operations may require elevated privileges.
    echo.
    pause
)

REM ============================================================================
REM STEP 1: Verify Docker Installation
REM ============================================================================
echo [1/7] Checking Docker installation...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH.
    echo Please install Docker Desktop for Windows from:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo Docker found:
docker --version
echo.

REM ============================================================================
REM STEP 2: Create .env from template
REM ============================================================================
echo [2/7] Setting up environment file...
if exist ".env" (
    echo .env file already exists. Skipping template copy.
    echo IMPORTANT: Review .env and update with your actual credentials.
) else (
    copy .env.template .env >nul
    echo Created .env from template.
    echo REQUIRED: Edit .env and add your API keys and credentials!
)
echo.

REM ============================================================================
REM STEP 3: Create necessary directories
REM ============================================================================
echo [3/7] Creating directory structure...

mkdir "domains\trading\hummingbot\conf" 2>nul
mkdir "domains\trading\hummingbot\logs" 2>nul
mkdir "domains\trading\hummingbot\data" 2>nul
mkdir "domains\trading\strategies" 2>nul
mkdir "models\local" 2>nul
mkdir "core\memory\checkpoints" 2>nul
mkdir "docs\sessions" 2>nul

REM Create .gitkeep files to preserve empty directories
type nul > "domains\trading\hummingbot\conf\.gitkeep"
type nul > "domains\trading\hummingbot\logs\.gitkeep"
type nul > "domains\trading\hummingbot\data\.gitkeep"
type nul > "models\local\.gitkeep"
type nul > "core\memory\checkpoints\.gitkeep"

echo Directory structure created.
echo.

REM ============================================================================
REM STEP 4: Validate docker-compose configuration
REM ============================================================================
echo [4/7] Validating docker-compose.yml...
docker-compose config >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: docker-compose.yml validation failed.
    echo Please check the file for syntax errors.
    pause
    exit /b 1
)
echo docker-compose.yml is valid.
echo.

REM ============================================================================
REM STEP 5: Pull Docker images (optional, can be slow)
REM ============================================================================
echo [5/7] Docker image setup...
echo.
choice /C YN /M "Pull Docker images now? (May take 10-30 minutes on first run)"
if %errorLevel%==1 (
    echo Pulling images...
    docker-compose pull
    echo.
) else (
    echo Skipping image pull. Images will download on first 'docker-compose up'.
    echo.
)

REM ============================================================================
REM STEP 6: Create backup directories
REM ============================================================================
echo [6/7] Setting up backup locations...

REM Check if external backup drive exists (from .env template default)
if exist "E:\" (
    mkdir "E:\Rhiz_Backups" 2>nul
    echo External backup directory: E:\Rhiz_Backups
) else (
    echo WARNING: External drive E:\ not found.
    echo Update BACKUP_EXTERNAL_PATH in .env with correct path.
)

REM Create OneDrive backup directory
mkdir "%USERPROFILE%\OneDrive\Rhiz_Backups" 2>nul
echo Cloud backup directory: %USERPROFILE%\OneDrive\Rhiz_Backups
echo.

REM ============================================================================
REM STEP 7: Initialize Git repository (if not already initialized)
REM ============================================================================
echo [7/7] Git repository setup...
if exist ".git" (
    echo Git repository already initialized.
) else (
    choice /C YN /M "Initialize Git repository?"
    if %errorLevel%==1 (
        git init
        git add .gitignore README.md CLAUDE.md
        git commit -m "Initial commit: Rhiz project foundation"
        echo Git repository initialized.
    ) else (
        echo Skipping Git initialization.
    )
)
echo.

REM ============================================================================
REM INITIALIZATION COMPLETE
REM ============================================================================
echo ========================================
echo INITIALIZATION COMPLETE
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. Edit .env file with your API keys and credentials
echo    - HUMMINGBOT_PASSWORD (choose a strong password)
echo    - KRAKEN_API_KEY and KRAKEN_SECRET_KEY
echo    - ANTHROPIC_API_KEY (if using Claude API directly)
echo.
echo 2. Start Docker services:
echo    docker-compose up -d
echo.
echo 3. Attach to Hummingbot:
echo    docker attach rhiz_hummingbot
echo    (Detach: Ctrl+P, Ctrl+Q)
echo.
echo 4. Verify LocalAI:
echo    curl http://localhost:8080/readyz
echo.
echo 5. Review architectural framework:
echo    C:\Users\dread\RHIZ_ARCHITECTURAL_FRAMEWORK.md
echo.
echo 6. Load session checkpoint in Claude Code:
echo    - Navigate to Rhiz_LocalDev directory
echo    - Reference CLAUDE.md for project context
echo.
echo ========================================
echo.
pause
