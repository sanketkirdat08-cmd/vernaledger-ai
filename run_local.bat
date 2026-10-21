@echo off
title VernaLedger.AI - Local Server
echo ========================================================
echo   Starting VernaLedger.AI Local Server...
echo ========================================================

cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python app.py
pause
