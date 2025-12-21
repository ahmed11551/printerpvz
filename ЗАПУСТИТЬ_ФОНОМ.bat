@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Запуск сервера в фоновом режиме (без окна консоли)
start /min "" pythonw.exe server.py 2>nul

:: Если pythonw.exe не найден, пытаемся через python с минимизированным окном
if errorlevel 1 (
    start /min "" python server.py
)

