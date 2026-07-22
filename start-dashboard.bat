@echo off
echo ==========================================
echo   CodeForge - Dashboard Launcher
echo ==========================================
echo.

:: Check Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Install Node.js 18+: https://nodejs.org/
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "dashboard\node_modules" (
    echo [1/2] Installing dashboard dependencies...
    cd dashboard
    npm install
    cd ..
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo [1/2] Dependencies already installed.
)

echo [2/2] Starting Teacher Dashboard...
echo Dashboard: http://localhost:5173
echo.
echo Press Ctrl+C to stop.
echo.

cd dashboard
set VITE_SERVER_URL=http://192.168.1.1:8000
npm run dev
