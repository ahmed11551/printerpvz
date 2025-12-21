@echo off
REM Скрипт для настройки автозапуска сервера при старте Windows

echo ================================================
echo       НАСТРОЙКА АВТОЗАПУСКА СЕРВЕРА
echo ================================================
echo.

cd /d "%~dp0"

REM Получаем полный путь к скрипту запуска
set SCRIPT_PATH=%~dp0ЗАПУСТИТЬ_ПРОСТО.bat

REM Создаем VBS скрипт для запуска без окна
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\print_server_start.vbs"
echo WshShell.Run """%SCRIPT_PATH%""", 0, False >> "%TEMP%\print_server_start.vbs"

REM Создаем ярлык в автозагрузке
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT=%STARTUP%\Печать этикеток.lnk

REM Удаляем старый ярлык если есть
if exist "%SHORTCUT%" del "%SHORTCUT%"

REM Создаем новый ярлык
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'wscript.exe'; $Shortcut.Arguments = '""%TEMP%\print_server_start.vbs""'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo [OK] Автозапуск настроен успешно!
    echo.
    echo Сервер будет запускаться автоматически при включении Windows.
    echo.
    echo Для отключения автозапуска удалите ярлык:
    echo %SHORTCUT%
) else (
    echo [ОШИБКА] Не удалось создать ярлык автозапуска
    echo Попробуйте запустить от имени администратора
)

echo.
pause

