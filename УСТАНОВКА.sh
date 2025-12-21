#!/bin/bash
# Простая установка программы печати ячеек ПВЗ

clear
echo ""
echo "================================================"
echo "   УСТАНОВКА ПРОГРАММЫ ПЕЧАТИ ЯЧЕЕК ПВЗ"
echo "================================================"
echo ""

# Проверка Python
echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "[ОШИБКА] Python3 не найден!"
    echo ""
    echo "Установите:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-pip"
    echo ""
    exit 1
fi
echo "[OK] Python установлен"
echo ""

# Установка зависимостей
echo "Установка зависимостей..."
python3 -m pip install --quiet --upgrade pip 2>/dev/null
python3 -m pip install --quiet -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось установить зависимости"
    exit 1
fi
echo "[OK] Зависимости установлены"
echo ""

# Создание скрипта запуска
echo "Создание скрипта запуска..."
cat > ЗАПУСТИТЬ.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 server.py
EOF
chmod +x ЗАПУСТИТЬ.sh 2>/dev/null
echo "[OK] Скрипт запуска создан"
echo ""

echo "================================================"
echo "          УСТАНОВКА ЗАВЕРШЕНА!"
echo "================================================"
echo ""
echo "ЧТО ДАЛЬШЕ:"
echo ""
echo "1. Настройте принтер (откройте config.json и укажите порт)"
echo ""
echo "2. Запустите сервер: ./ЗАПУСТИТЬ.sh"
echo ""
echo "3. Установите расширение в браузере:"
echo "   - Откройте chrome://extensions/"
echo "   - Включите 'Режим разработчика'"
echo "   - Нажмите 'Загрузить распакованное расширение'"
echo "   - Выберите эту папку"
echo ""
echo "================================================"
echo ""

