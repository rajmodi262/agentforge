@echo off
SETLOCAL EnableDelayedExpansion
title AgentForge AI Launcher

echo ===================================================
echo     AgentForge AI - Initialization ^& Startup
echo ===================================================
echo.

cd /d "%~dp0"

:: Step 1: Backend Setup
echo [1/4] Checking Backend Environment...
cd backend
if not exist "venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment. Please ensure Python is installed and added to PATH.
        pause
        exit /b 1
    )
)

echo [2/4] Checking Backend Dependencies...
call venv\Scripts\activate.bat

:: Check if uvicorn exists to avoid reinstalling every time
if not exist "venv\Scripts\uvicorn.exe" (
    echo Installing backend dependencies...
    python -m pip install --upgrade pip >nul 2>&1
    :: --no-cache-dir keeps memory low on small machines
    pip install --no-cache-dir -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install core Python dependencies.
        pause
        exit /b 1
    )
    :: Optional vector-RAG deps are heavy ^(torch^); failure here is non-fatal.
    echo Installing optional RAG dependencies ^(skippable^)...
    pip install --no-cache-dir -r requirements-optional.txt
    if errorlevel 1 (
        echo Warning: Optional RAG/vector-store deps were not installed ^(likely low memory^).
        echo The app will run normally with RAG disabled. Continuing...
    )
) else (
    echo Backend dependencies already installed.
)

:: Step 3: Frontend Setup
cd ..\frontend
echo [3/4] Checking Frontend Dependencies...
if not exist "node_modules\" (
    echo Installing Node modules. This might take a minute...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install npm dependencies. Please ensure Node.js is installed.
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed.
)

:: Step 4: Start Servers
echo [4/4] Starting Servers...

echo Starting FastAPI Backend...
start "AgentForge Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

echo Starting React Frontend...
start "AgentForge Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===================================================
echo   Startup Complete!
echo   - Backend is opening in a new window.
echo   - Frontend is opening in a new window.
echo.
echo   Once both are ready, you can access the UI at:
echo   http://localhost:5173
echo ===================================================
echo.
pause
