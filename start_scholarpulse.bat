@echo off
echo ========================================
echo ScholarPulse - Full Stack Startup
echo ========================================
echo.
echo This script will start both the Django backend and Streamlit frontend.
echo.

cd /d %~dp0

echo Step 1: Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Step 2: Setting up Django database...
cd backend
python manage.py makemigrations research --no-input 2>nul
python manage.py migrate --no-input
cd ..

echo.
echo Step 3: Starting servers...
echo.

start "ScholarPulse Backend" cmd /k "cd /d %~dp0backend && python manage.py runserver 0.0.0.0:8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

start "ScholarPulse Frontend" cmd /k "cd /d %~dp0frontend && streamlit run app.py --server.port 8501"

echo.
echo ========================================
echo Both servers are starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo Admin: http://localhost:8000/admin
echo API Health: http://localhost:8000/api/health/
echo ========================================
echo.
pause
