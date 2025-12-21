@echo off
chcp 65001 >nul
title Печать этикеток ячеек ПВЗ - GUI
color 0B
cls

cd /d "%~dp0"

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Запуск GUI приложения
python app_gui.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось запустить приложение
    pause
)

