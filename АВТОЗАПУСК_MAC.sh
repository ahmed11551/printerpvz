#!/bin/bash

echo "================================================"
echo "     НАСТРОЙКА АВТОЗАПУСКА СЕРВЕРА (macOS)"
echo "================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_NAME="com.printserver.autostart.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Создание plist файла..."

cat > /tmp/$PLIST_NAME << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.printserver.autostart</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$SCRIPT_DIR/ЗАПУСТИТЬ.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
</dict>
</plist>
EOF

# Копируем в LaunchAgents
mkdir -p "$HOME/Library/LaunchAgents"
cp /tmp/$PLIST_NAME "$PLIST_PATH"

# Загружаем в launchd
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

if [ $? -eq 0 ]; then
    echo "[OK] Автозапуск настроен успешно!"
    echo ""
    echo "Сервер будет запускаться автоматически при входе в систему."
    echo ""
    echo "Для отключения автозапуска выполните:"
    echo "  launchctl unload $PLIST_PATH"
    echo "  rm $PLIST_PATH"
else
    echo "[ОШИБКА] Не удалось настроить автозапуск"
    exit 1
fi

echo ""
echo "Готово!"

