@echo off
echo ========================================
echo   Bulk WhatsApp Sender - Installation
echo ========================================
echo.
echo This script will install all required dependencies.
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python is installed!
echo.
echo Installing required packages...
echo This may take a few minutes...
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now run the application using:
echo   - Double-click run.bat
echo   - Or run: python app.py
echo.
echo Then open your browser and go to:
echo   http://127.0.0.1:5000
echo.
pause

