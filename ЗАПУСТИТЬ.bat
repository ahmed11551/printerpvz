@echo off
chcp 65001 >nul
title Сервер печати ячеек ПВЗ
color 0B
cls

echo.
echo ================================================
echo     СЕРВЕР ПЕЧАТИ ЯЧЕЕК ПВЗ
echo ================================================
echo.
echo [1] Запуск сервера...
echo.

cd /d "%~dp0"

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Проверка зависимостей
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Зависимости не установлены!
    echo.
    echo Запустите сначала УСТАНОВКА.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Python найден
echo [OK] Зависимости установлены
echo.
echo ================================================
echo     СЕРВЕР ЗАПУСКАЕТСЯ...
echo ================================================
echo.
echo Сервер будет доступен на: http://localhost:5001
echo.
echo Для остановки нажмите Ctrl+C
echo.
echo ================================================
echo.

python server.py

pause
