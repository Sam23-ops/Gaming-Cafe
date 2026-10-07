@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM GAMMERS ADDA - Session Start Checker
REM ═══════════════════════════════════════════════════════════════════════════════
REM This script checks for bookings that should start now and sends notifications.
REM 
REM HOW TO USE:
REM 1. Run manually: double-click this file
REM 2. Schedule via Task Scheduler (Windows):
REM    - Open Task Scheduler
REM    - Create Basic Task
REM    - Trigger: Daily, repeat every 1 minute
REM    - Action: Start a program -> Browse to this .bat file
REM
REM ═══════════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
python manage.py check_session_starts
pause
