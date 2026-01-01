@echo off
echo ========================================
echo   Fixing 403 Error - Troubleshooting
echo ========================================
echo.

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python first.
    pause
    exit /b 1
)
echo Python is installed.
echo.

echo Step 2: Installing/Updating dependencies...
pip install -r requirements.txt --quiet
echo Dependencies installed.
echo.

echo Step 3: Testing Flask with simple server...
echo.
echo Starting test server on port 5000...
echo Open http://localhost:5000 in your browser
echo.
echo If test server works, the issue is with the main app.
echo If test server also gives 403, it's a system/browser issue.
echo.
echo Press any key to start test server...
pause >nul

python test_server.py

