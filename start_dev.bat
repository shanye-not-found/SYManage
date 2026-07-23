@echo off
echo ========================================
echo Starting SYManage Development Environment
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting backend...
start "SYManage Backend" cmd /k "cd backend && call conda activate SYManage && fastapi dev app/main.py"

timeout /t 5 /nobreak >nul

echo [2/2] Starting frontend...
start "SYManage Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Started successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Note: Close service windows with Ctrl+C
pause
