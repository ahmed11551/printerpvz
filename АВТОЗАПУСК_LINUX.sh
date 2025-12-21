#!/bin/bash

echo "================================================"
echo "     НАСТРОЙКА АВТОЗАПУСКА СЕРВЕРА (Linux)"
echo "================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_NAME="print-server.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "Создание systemd service файла..."

# Проверяем права root
if [ "$EUID" -ne 0 ]; then 
    echo "Для создания системного сервиса нужны права root."
    echo "Запустите скрипт с sudo:"
    echo "  sudo $0"
    exit 1
fi

cat > /tmp/$SERVICE_NAME << EOF
[Unit]
Description=Print Server for PВЗ
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Копируем файл сервиса
cp /tmp/$SERVICE_NAME "$SERVICE_FILE"

# Перезагружаем systemd и включаем автозапуск
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

if [ $? -eq 0 ]; then
    echo "[OK] Автозапуск настроен успешно!"
    echo ""
    echo "Сервер будет запускаться автоматически при загрузке системы."
    echo ""
    echo "Управление сервисом:"
    echo "  sudo systemctl start $SERVICE_NAME   - запустить"
    echo "  sudo systemctl stop $SERVICE_NAME    - остановить"
    echo "  sudo systemctl status $SERVICE_NAME  - статус"
    echo "  sudo systemctl disable $SERVICE_NAME - отключить автозапуск"
else
    echo "[ОШИБКА] Не удалось настроить автозапуск"
    exit 1
fi

echo ""
echo "Готово!"

