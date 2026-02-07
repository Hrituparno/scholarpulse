@echo off
echo ========================================
echo ScholarPulse - Django Backend Startup
echo ========================================
echo.

cd /d %~dp0backend

echo Installing/checking dependencies...
pip install django djangorestframework django-cors-headers -q

echo.
echo Creating database migrations...
python manage.py makemigrations research --no-input 2>nul
python manage.py migrate --no-input

echo.
echo Starting Django development server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python manage.py runserver 0.0.0.0:8000
