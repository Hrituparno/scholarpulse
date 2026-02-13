@echo off
title ScholarPulse - Local Development
color 0B

echo ========================================
echo   ScholarPulse - Local Development
echo ========================================
echo.
echo Starting backend and frontend for local testing...
echo.

REM Start Django Backend
echo [1/2] Starting Django Backend on port 8000...
start "Backend" cmd /k "cd backend && python manage.py runserver 8000"
timeout /t 3 /nobreak >nul

REM Start Streamlit Frontend
echo [2/2] Starting Streamlit Frontend on port 8501...
start "Frontend" cmd /k "set SCHOLARPULSE_API_URL=http://localhost:8000 && streamlit run frontend/app.py --server.port 8501"

echo.
echo ========================================
echo   Local Development Started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to exit this window...
echo (Services will keep running in their own windows)
pause >nul
