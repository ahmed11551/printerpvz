#!/bin/bash
# Автоматическая установка расширения браузера

clear
echo ""
echo "================================================"
echo "   АВТОМАТИЧЕСКАЯ УСТАНОВКА РАСШИРЕНИЯ"
echo "================================================"
echo ""

# Определяем путь к папке extension
EXTENSION_PATH="$(cd "$(dirname "$0")" && pwd)/extension"

if [ ! -d "$EXTENSION_PATH" ]; then
    echo "[ОШИБКА] Папка 'extension' не найдена!"
    echo "Убедитесь, что вы запускаете скрипт из корневой папки проекта."
    echo ""
    exit 1
fi

echo "Папка расширения найдена: $EXTENSION_PATH"
echo ""

# Открываем страницы расширений
echo "Открываю страницы расширений..."
echo ""

# Chrome (macOS)
if command -v open &> /dev/null; then
    echo "[1] Открываю Chrome..."
    open "chrome://extensions/" 2>/dev/null
    sleep 1
fi

# Яндекс.Браузер (macOS)
if command -v open &> /dev/null; then
    echo "[2] Открываю Яндекс.Браузер..."
    open "browser://extensions/" 2>/dev/null
    sleep 1
fi

# Edge (macOS)
if command -v open &> /dev/null; then
    echo "[3] Открываю Edge..."
    open "edge://extensions/" 2>/dev/null
    sleep 1
fi

echo ""
echo "================================================"
echo "          ИНСТРУКЦИЯ ПО УСТАНОВКЕ"
echo "================================================"
echo ""
echo "В открывшемся окне браузера:"
echo ""
echo "1. Включите 'Режим разработчика' (переключатель справа вверху)"
echo ""
echo "2. Нажмите 'Загрузить распакованное расширение'"
echo ""
echo "3. Выберите папку: $EXTENSION_PATH"
echo ""
echo "4. Готово! Расширение установлено"
echo ""
echo "================================================"
echo ""
echo "ПРИМЕЧАНИЕ: Если страница не открылась автоматически,"
echo "скопируйте путь выше и откройте вручную:"
echo "chrome://extensions/ или browser://extensions/"
echo ""
read -p "Нажмите Enter для продолжения..."

