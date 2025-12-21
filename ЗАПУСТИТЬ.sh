#!/bin/bash
cd "$(dirname "$0")"

# Открываем браузер через 3 секунды (работает на macOS и Linux)
(sleep 3 && open "http://localhost:5001" 2>/dev/null || xdg-open "http://localhost:5001" 2>/dev/null) &

python3 server.py

