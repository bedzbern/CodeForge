@echo off
echo ==========================================
echo   CodeForge - Teacher PC Launcher
echo ==========================================
echo.

:: Check Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Install Python 3.10+: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "server\.deps_installed" (
    echo [1/3] Installing Python dependencies...
    pip install -r server\requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo done > server\.deps_installed
) else (
    echo [1/3] Dependencies already installed.
)

:: Set environment defaults
if not defined AI_PROVIDER set AI_PROVIDER=groq
if not defined TEACHER_IP set TEACHER_IP=192.168.1.1
if not defined GROQ_API_KEY set GROQ_API_KEY=

echo.
echo [2/3] Configuration:
echo   AI Provider: %AI_PROVIDER%
echo   Teacher IP:  %TEACHER_IP%
echo.

echo [3/3] Starting CodeForge server on port 8000...
echo Dashboard URL: http://localhost:5173
echo API docs:      http://192.168.1.1:8000/docs
echo.
echo Press Ctrl+C to stop.
echo.

python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
