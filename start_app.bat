@echo off
title Bulk WhatsApp Sender
color 0A
echo.
echo ========================================
echo   Bulk WhatsApp Sender
echo   Starting Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Flask not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies are installed
)
echo.

REM Check if templates folder exists
if not exist "templates\index.html" (
    echo [ERROR] templates\index.html not found!
    echo Please ensure the file exists.
    pause
    exit /b 1
)
echo [OK] Template file found
echo.

REM Check if uploads folder exists
if not exist "uploads" (
    echo [INFO] Creating uploads folder...
    mkdir uploads
)
echo [OK] Uploads folder ready
echo.

echo ========================================
echo   Starting Flask Server...
echo ========================================
echo.
echo The server will be available at:
echo   - http://localhost:5000
echo   - http://127.0.0.1:5000
echo.
echo Test route: http://localhost:5000/test
echo.
echo If you get a 403 error:
echo   1. Try http://localhost:5000 instead of 127.0.0.1
echo   2. Try a different browser (Chrome, Firefox, Edge)
echo   3. Try incognito/private mode
echo   4. Check FIX_403_ERROR.md for detailed solutions
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start!
    echo.
    echo Common issues:
    echo   - Port 5000 already in use (close other applications)
    echo   - Missing dependencies (run: pip install -r requirements.txt)
    echo   - Python not in PATH
    echo.
    pause
)

