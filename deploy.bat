@echo off
REM ScholarPulse Deployment Helper Script
REM Automates pre-deployment checks and git operations

echo ============================================================
echo ScholarPulse - Deployment Helper
echo ============================================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] Running API tests...
python test_groq_api.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] API tests failed. Fix issues before deploying.
    echo Continue anyway? (y/n)
    set /p continue=
    if /i not "%continue%"=="y" exit /b 1
)

echo.
echo [2/6] Checking for uncommitted changes...
git status --short
echo.

echo [3/6] Adding all changes...
git add .

echo.
echo [4/6] Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update: Production-ready deployment with Groq API fixes

git commit -m "%commit_msg%"
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] No changes to commit or commit failed
)

echo.
echo [5/6] Pushing to GitHub...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Push failed. Check your git configuration.
    pause
    exit /b 1
)

echo.
echo [6/6] Deployment checklist...
echo.
echo ============================================================
echo Next Steps:
echo ============================================================
echo.
echo 1. RENDER (Backend):
echo    - Go to: https://dashboard.render.com/
echo    - Your service should auto-deploy from GitHub
echo    - Monitor logs for any errors
echo    - Test: https://your-app.onrender.com/api/health/
echo.
echo 2. STREAMLIT CLOUD (Frontend):
echo    - Go to: https://share.streamlit.io/
echo    - Redeploy your app if needed
echo    - Verify SCHOLARPULSE_API_URL is set correctly
echo.
echo 3. VERIFY DEPLOYMENT:
echo    - Run: python debug_production.py
echo    - Test a research query
echo    - Check logs for errors
echo.
echo ============================================================
echo Deployment initiated successfully!
echo ============================================================
echo.

pause
