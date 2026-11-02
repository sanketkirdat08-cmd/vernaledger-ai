@echo off
chcp 65001 > nul
title VernaLedger.AI - Local Server
echo ========================================================
echo   Starting VernaLedger.AI Local Server...
echo ========================================================

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" app.py
) else (
    python app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server encountered an error.
    pause
)
