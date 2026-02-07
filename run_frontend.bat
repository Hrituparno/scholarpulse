@echo off
echo ========================================
echo ScholarPulse - Streamlit Frontend Startup
echo ========================================
echo.

cd /d %~dp0frontend

echo Starting Streamlit on http://localhost:8501
echo Make sure the Django backend is running first!
echo Press Ctrl+C to stop
echo.
streamlit run app.py --server.port 8501
