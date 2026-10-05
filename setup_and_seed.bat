@echo off
title Gammers Adda - Setup and Database Seed
echo ========================================================
echo  GAMMERS ADDA - GAMING CAFE PLATFORM SETUP
echo ========================================================
echo.

set PYTHON_CMD=C:\Users\Nibedita\AppData\Local\Python\pythoncore-3.14-64\python.exe

if not exist "%PYTHON_CMD%" (
    echo Python not found at default location, trying python from PATH...
    set PYTHON_CMD=python
)

echo [1/4] Running Django System Diagnostics...
"%PYTHON_CMD%" manage.py check
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] System check encountered issues.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/4] Generating Database Migrations...
"%PYTHON_CMD%" manage.py makemigrations core accounts venue games pricing bookings payments engagement --noinput

echo.
echo [3/4] Applying Migrations to SQLite Database...
"%PYTHON_CMD%" manage.py migrate --noinput

echo.
echo [4/4] Seeding Master Database with Demo Data...
"%PYTHON_CMD%" seed_data.py

echo.
echo ========================================================
echo  SETUP COMPLETED SUCCESSFULLY!
echo ========================================================
echo Super Admin Login: admin / admin123
echo Staff Login:       staff / staff123
echo Customer Login:    gamer1 / gamer123
echo.
pause
