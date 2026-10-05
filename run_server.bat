@echo off
title Gammers Adda Development Server
echo ========================================================
echo  GAMMERS ADDA - PLAY * ENJOY * CONNECT
echo  Starting local development server on http://127.0.0.1:8000/
echo ========================================================
echo.

set PYTHON_CMD=C:\Users\Nibedita\AppData\Local\Python\pythoncore-3.14-64\python.exe

if not exist "%PYTHON_CMD%" (
    set PYTHON_CMD=python
)

"%PYTHON_CMD%" manage.py runserver 127.0.0.1:8000
pause
