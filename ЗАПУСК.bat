@echo off
chcp 65001 >nul
title Печать ячеек ПВЗ - Запуск
color 0A
cls

:MENU
echo.
echo ================================================
echo        ПЕЧАТЬ ЯЧЕЕК ПВЗ - ГЛАВНОЕ МЕНЮ
echo ================================================
echo.
echo [1] Запустить сервер
echo [2] Проверить статус сервера
echo [3] Открыть настройки принтера (config.json)
echo [4] Установить расширение в браузере
echo [5] Тестовая печать
echo [6] Открыть документацию
echo [0] Выход
echo.
echo ================================================
set /p choice="Выберите действие (0-6): "

if "%choice%"=="1" goto START_SERVER
if "%choice%"=="2" goto CHECK_STATUS
if "%choice%"=="3" goto OPEN_CONFIG
if "%choice%"=="4" goto INSTALL_EXTENSION
if "%choice%"=="5" goto TEST_PRINT
if "%choice%"=="6" goto OPEN_DOCS
if "%choice%"=="0" goto EXIT

echo.
echo [ОШИБКА] Неверный выбор!
timeout /t 2 >nul
goto MENU

:START_SERVER
cls
echo.
echo ================================================
echo          ЗАПУСК СЕРВЕРА...
echo ================================================
echo.
cd /d "%~dp0"
call "ЗАПУСТИТЬ.bat"
goto MENU

:CHECK_STATUS
cls
echo.
echo ================================================
echo          ПРОВЕРКА СТАТУСА...
echo ================================================
echo.
curl -s http://localhost:5001/status >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Сервер не запущен!
    echo.
    echo Запустите сервер через пункт [1]
) else (
    echo [OK] Сервер работает!
    echo.
    curl -s http://localhost:5001/status
)
echo.
pause
goto MENU

:OPEN_CONFIG
cls
echo.
echo ================================================
echo       ОТКРЫТИЕ НАСТРОЕК ПРИНТЕРА...
echo ================================================
echo.
cd /d "%~dp0"
if exist config.json (
    start notepad config.json
    echo [OK] Файл config.json открыт в блокноте
) else (
    echo [ОШИБКА] Файл config.json не найден!
)
echo.
pause
goto MENU

:INSTALL_EXTENSION
cls
echo.
echo ================================================
echo       УСТАНОВКА РАСШИРЕНИЯ В БРАУЗЕРЕ
echo ================================================
echo.
echo 1. Откроется страница расширений Chrome
echo 2. Включите "Режим разработчика" (справа вверху)
echo 3. Нажмите "Загрузить распакованное расширение"
echo 4. Выберите эту папку
echo.
pause
start chrome://extensions/
timeout /t 2 >nul
start edge://extensions/
echo.
echo [OK] Страницы расширений открыты
echo.
pause
goto MENU

:TEST_PRINT
cls
echo.
echo ================================================
echo            ТЕСТОВАЯ ПЕЧАТЬ
echo ================================================
echo.
curl -s http://localhost:5001/status >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Сервер не запущен!
    echo.
    echo Сначала запустите сервер через пункт [1]
) else (
    echo Отправка тестовой печати...
    curl -X POST http://localhost:5001/test -s
    echo.
    echo.
    echo [OK] Тестовая печать отправлена!
    echo Проверьте принтер
)
echo.
pause
goto MENU

:OPEN_DOCS
cls
echo.
echo ================================================
echo            ДОКУМЕНТАЦИЯ
echo ================================================
echo.
cd /d "%~dp0"
if exist "ПРОСТАЯ_УСТАНОВКА.txt" (
    start notepad "ПРОСТАЯ_УСТАНОВКА.txt"
    echo [OK] Инструкция открыта
) else (
    echo [ОШИБКА] Файл документации не найден
)
echo.
pause
goto MENU

:EXIT
cls
echo.
echo До свидания!
timeout /t 1 >nul
exit

