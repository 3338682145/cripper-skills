@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-to-codex.ps1"
if errorlevel 1 pause
