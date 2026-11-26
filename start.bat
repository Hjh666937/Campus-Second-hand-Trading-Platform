@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Campus Trade - Start All
echo   Backend : http://127.0.0.1:5000
echo   Frontend: http://localhost:2064
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found in PATH
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] node not found in PATH
    pause
    exit /b 1
)

netstat -ano | findstr ":5000 " | findstr "LISTENING" >nul
if not errorlevel 1 echo [WARN] port 5000 is already in use

netstat -ano | findstr ":2064 " | findstr "LISTENING" >nul
if not errorlevel 1 echo [WARN] port 2064 is already in use

echo.
echo [1/2] Starting Flask backend (background)...

cd backend
start /min pythonw app.py
cd ..

echo Waiting for backend...
timeout /t 3 /nobreak >nul

echo [2/2] Starting Vite frontend...
echo       Browser will open http://localhost:2064/login
echo.

cd frontend
call npm run dev

echo.
echo Frontend stopped.
pause
