@echo off
title VernaLedger.AI - Local Server
echo ========================================================
echo   Starting VernaLedger.AI Local Server...
echo ========================================================

cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Opening http://localhost:8000 in your browser...
start http://localhost:8000

python app.py
pause
