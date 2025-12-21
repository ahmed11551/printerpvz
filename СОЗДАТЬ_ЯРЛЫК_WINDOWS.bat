@echo off
REM Скрипт для создания ярлыка на рабочем столе

echo ================================================
echo    СОЗДАНИЕ ЯРЛЫКА НА РАБОЧЕМ СТОЛЕ
echo ================================================
echo.

cd /d "%~dp0"

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\Печать этикеток.lnk
set TARGET=%~dp0ЗАПУСТИТЬ_ПРОСТО.bat

REM Удаляем старый ярлык если есть
if exist "%SHORTCUT%" del "%SHORTCUT%"

REM Создаем ярлык через PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'cmd.exe'; $Shortcut.Arguments = '/c \"\"%TARGET%\"\"'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,137'; $Shortcut.Description = 'Запуск сервера печати этикеток ПВЗ'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo [OK] Ярлык создан успешно!
    echo.
    echo Ярлык находится на рабочем столе:
    echo %SHORTCUT%
    echo.
    echo Теперь вы можете запускать сервер двойным кликом по ярлыку.
) else (
    echo [ОШИБКА] Не удалось создать ярлык
)

echo.
pause

