@echo off
chcp 65001 > nul
title VernaLedger.AI - GitOps Real-Time Auto Sync Daemon (Every 4s)
echo ========================================================
echo   Starting VernaLedger.AI GitOps Auto-Sync Daemon...
echo   Commits locally (100%% Offline) and pushes to GitHub
echo ========================================================

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" git_auto_sync.py
) else (
    python git_auto_sync.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Git auto-sync daemon exited.
    pause
)
