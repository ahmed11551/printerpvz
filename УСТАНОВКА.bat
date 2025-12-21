@echo off
chcp 65001 >nul
title Установка программы печати ячеек ПВЗ
color 0A
cls

echo.
echo ================================================
echo    УСТАНОВКА ПРОГРАММЫ ПЕЧАТИ ЯЧЕЕК ПВЗ
echo ================================================
echo.

:: Проверка Python
echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python: https://www.python.org/downloads/
    echo При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo [OK] Python установлен
echo.

:: Установка зависимостей
echo Установка зависимостей...
python -m pip install --quiet --upgrade pip >nul 2>&1
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости
    pause
    exit /b 1
)
echo [OK] Зависимости установлены
echo.

:: Создание ярлыка запуска
echo Создание ярлыка запуска...
if not exist "ЗАПУСТИТЬ.bat" (
    (
        echo @echo off
        echo cd /d "%%~dp0"
        echo python server.py
        echo pause
    ) > ЗАПУСТИТЬ.bat
)
echo [OK] Ярлык создан
echo.

echo ================================================
echo           УСТАНОВКА ЗАВЕРШЕНА!
echo ================================================
echo.
echo ЧТО ДАЛЬШЕ:
echo.
echo 1. Настройте принтер (откройте config.json и укажите порт)
echo.
echo 2. Запустите сервер: двойной клик на ЗАПУСТИТЬ.bat
echo.
echo 3. Установите расширение в браузере:
echo    - Откройте chrome://extensions/
echo    - Включите "Режим разработчика"
echo    - Нажмите "Загрузить распакованное расширение"
echo    - Выберите эту папку
echo.
echo ================================================
echo.
pause

