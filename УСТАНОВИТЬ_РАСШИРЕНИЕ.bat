@echo off
chcp 65001 >nul
title Установка расширения браузера
color 0E
cls

echo.
echo ================================================
echo    АВТОМАТИЧЕСКАЯ УСТАНОВКА РАСШИРЕНИЯ
echo ================================================
echo.

:: Определяем путь к папке extension
set "EXTENSION_PATH=%~dp0extension"

if not exist "%EXTENSION_PATH%" (
    echo [ОШИБКА] Папка 'extension' не найдена!
    echo Убедитесь, что вы запускаете скрипт из корневой папки проекта.
    echo.
    pause
    exit /b 1
)

echo Папка расширения найдена: %EXTENSION_PATH%
echo.

:: Открываем страницы расширений для разных браузеров
echo Открываю страницы расширений...
echo.

:: Chrome
echo [1] Открываю Chrome...
start chrome://extensions/ 2>nul
timeout /t 1 >nul

:: Яндекс.Браузер
echo [2] Открываю Яндекс.Браузер...
start browser://extensions/ 2>nul
timeout /t 1 >nul

:: Edge
echo [3] Открываю Edge...
start edge://extensions/ 2>nul
timeout /t 1 >nul

echo.
echo ================================================
echo           ИНСТРУКЦИЯ ПО УСТАНОВКЕ
echo ================================================
echo.
echo В открывшемся окне браузера:
echo.
echo 1. Включите "Режим разработчика" (переключатель справа вверху)
echo.
echo 2. Нажмите "Загрузить распакованное расширение"
echo.
echo 3. Выберите папку: %EXTENSION_PATH%
echo.
echo 4. Готово! Расширение установлено
echo.
echo ================================================
echo.
echo ПРИМЕЧАНИЕ: Если страница не открылась автоматически,
echo скопируйте путь выше и откройте вручную:
echo chrome://extensions/ или browser://extensions/
echo.
pause

