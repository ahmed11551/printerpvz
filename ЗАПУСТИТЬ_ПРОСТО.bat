@echo off
chcp 65001 >nul
title Печать ячеек ПВЗ
cd /d "%~dp0"

REM Открываем браузер через 3 секунды
start "" "http://localhost:5001" && timeout /t 3 /nobreak >nul

python server.py

