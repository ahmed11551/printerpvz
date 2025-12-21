@echo off
chcp 65001 >nul
title Настройка автозапуска сервера
color 0B
cls

echo ========================================
echo  НАСТРОЙКА АВТОЗАПУСКА СЕРВЕРА
echo ========================================
echo.

cd /d "%~dp0"

echo Выберите действие:
echo.
echo [1] Включить автозапуск сервера (GUI версия)
echo [2] Включить автозапуск сервера (консольная версия)
echo [3] Отключить автозапуск
echo [4] Проверить статус автозапуска
echo [5] Выход
echo.

set /p choice="Ваш выбор (1-5): "

if "%choice%"=="1" goto gui_autostart
if "%choice%"=="2" goto console_autostart
if "%choice%"=="3" goto disable_autostart
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto end
goto invalid

:gui_autostart
echo.
echo Настройка автозапуска GUI версии...
echo.

set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "script_name=Запуск_Печать_Ячеек_ПВЗ.bat"

:: Создаем скрипт автозапуска
(
echo @echo off
echo cd /d "%~dp0"
echo start "" "%~dp0ЗАПУСТИТЬ_GUI.bat"
) > "%startup_folder%\%script_name%"

if exist "%startup_folder%\%script_name%" (
    echo ✓ Автозапуск GUI версии включен!
    echo   Сервер будет запускаться автоматически при включении компьютера.
) else (
    echo ✗ Ошибка: не удалось создать файл автозапуска
)
goto end

:console_autostart
echo.
echo Настройка автозапуска консольной версии...
echo.

set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "script_name=Запуск_Печать_Ячеек_ПВЗ.bat"

:: Получаем полный путь к текущей папке
set "current_dir=%~dp0"
set "current_dir=%current_dir:~0,-1%"

:: Создаем скрипт автозапуска
(
echo @echo off
echo cd /d "%current_dir%"
echo start "Печать ячеек ПВЗ" "%current_dir%\ЗАПУСТИТЬ.bat"
) > "%startup_folder%\%script_name%"

if exist "%startup_folder%\%script_name%" (
    echo ✓ Автозапуск консольной версии включен!
    echo   Сервер будет запускаться автоматически при включении компьютера.
) else (
    echo ✗ Ошибка: не удалось создать файл автозапуска
)
goto end

:disable_autostart
echo.
echo Отключение автозапуска...
echo.

set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "script_name=Запуск_Печать_Ячеек_ПВЗ.bat"

if exist "%startup_folder%\%script_name%" (
    del "%startup_folder%\%script_name%"
    echo ✓ Автозапуск отключен!
) else (
    echo ⚠ Автозапуск не был включен.
)
goto end

:check_status
echo.
echo Проверка статуса автозапуска...
echo.

set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "script_name=Запуск_Печать_Ячеек_ПВЗ.bat"

if exist "%startup_folder%\%script_name%" (
    echo ✓ Автозапуск ВКЛЮЧЕН
    echo   Файл: %startup_folder%\%script_name%
    echo.
    echo Для отключения запустите этот скрипт и выберите пункт [3]
) else (
    echo ⚠ Автозапуск ОТКЛЮЧЕН
    echo.
    echo Для включения выберите пункт [1] или [2]
)
goto end

:invalid
echo.
echo ✗ Неверный выбор. Попробуйте снова.
goto end

:end
echo.
pause

