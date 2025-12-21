@echo off
chcp 65001 >nul
title Создание исполняемого файла (EXE)
color 0B
cls

echo.
echo ================================================
echo   СОЗДАНИЕ ИСПОЛНЯЕМОГО ФАЙЛА (EXE)
echo ================================================
echo.
echo Этот скрипт создаст EXE-файл, который не требует
echo установки Python на компьютере пользователя.
echo.
echo ВНИМАНИЕ: Для создания EXE требуется Python!
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Проверка config.json
if not exist "config.json" (
    echo [ОШИБКА] Файл config.json не найден!
    echo Убедитесь, что вы запускаете скрипт из папки проекта.
    pause
    exit /b 1
)

:: Проверка PyInstaller
echo Проверка PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не найден. Устанавливаю...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Очистка предыдущих сборок...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "Печать_Ячеек_ПВЗ.spec" del /q "Печать_Ячеек_ПВЗ.spec"

echo.
echo Создание EXE-файла...
echo Это может занять несколько минут...
echo.

:: Используем spec-файл если есть, иначе создаем через параметры
if exist "server.spec" (
    echo Используется server.spec для сборки...
    python -m PyInstaller server.spec --clean
) else (
    echo Создание EXE через PyInstaller...
    python -m PyInstaller --onefile --console --name "Печать_Ячеек_ПВЗ" --add-data "config.json;." server.py
)

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось создать EXE-файл
    echo Проверьте сообщения об ошибках выше
    pause
    exit /b 1
)

echo.
echo ================================================
echo           EXE-ФАЙЛ СОЗДАН!
echo ================================================
echo.

:: Проверка существования EXE
if exist "dist\Печать_Ячеек_ПВЗ.exe" (
    echo Файл создан: dist\Печать_Ячеек_ПВЗ.exe
    echo.
    echo Копирование необходимых файлов в папку dist...
    
    :: Копируем config.json если его там нет
    if not exist "dist\config.json" copy "config.json" "dist\"
    
    :: Копируем скрипт запуска
    copy "ЗАПУСТИТЬ_EXE.bat" "dist\" >nul 2>&1
    
    :: Копируем README и инструкции
    copy "README.md" "dist\" >nul 2>&1
    copy "INSTALL_RU.md" "dist\" >nul 2>&1
    copy "ИНСТРУКЦИЯ_EXE.md" "dist\" >nul 2>&1
    
    echo.
    echo ================================================
    echo         ГОТОВО К РАСПРОСТРАНЕНИЮ!
    echo ================================================
    echo.
    echo ВАЖНО ДЛЯ ПОЛЬЗОВАТЕЛЯ:
    echo.
    echo 1. Скопируйте ВСЮ папку 'dist' пользователю
    echo    (или только файл Печать_Ячеек_ПВЗ.exe + config.json)
    echo.
    echo 2. Пользователь должен:
    echo    - Настроить config.json (указать порт принтера)
    echo    - Установить расширение браузера (см. README.md)
    echo    - Запустить ЗАПУСТИТЬ_EXE.bat (или Печать_Ячеек_ПВЗ.exe напрямую)
    echo.
    echo 3. Расширение браузера нужно установить отдельно
    echo    (файлы: manifest.json, content.js, popup.js, background.js, icons)
    echo.
    echo Папка dist готова к распространению!
    echo.
) else (
    echo [ОШИБКА] EXE-файл не найден в папке dist!
    echo Проверьте сообщения об ошибках выше
)

pause

