#!/bin/bash
# Запуск GUI приложения

cd "$(dirname "$0")"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ОШИБКА] Python3 не найден!"
    echo "Установите Python3"
    exit 1
fi

# Запуск GUI приложения
python3 app_gui.py

