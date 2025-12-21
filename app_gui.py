#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Графический интерфейс для программы печати ячеек ПВЗ
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
import json
import os
import subprocess
import sys
from pathlib import Path

# Импортируем сервер
try:
    import server
except ImportError:
    messagebox.showerror("Ошибка", "Не найден файл server.py!\nУбедитесь, что все файлы на месте.")
    sys.exit(1)


class PrintServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Печать этикеток ячеек ПВЗ")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Переменные
        self.server_thread = None
        self.server_running = False
        self.update_id = None
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Запускаем обновление статуса
        self.update_status()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # Кнопка запуска/остановки сервера
        self.start_btn = ttk.Button(
            top_frame, 
            text="▶ Запустить сервер", 
            command=self.toggle_server,
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка открытия настроек
        ttk.Button(
            top_frame, 
            text="⚙ Настройки принтера", 
            command=self.open_printer_settings,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка установки расширения
        ttk.Button(
            top_frame, 
            text="🌐 Установить расширение", 
            command=self.install_extension,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка веб-интерфейса
        ttk.Button(
            top_frame, 
            text="📊 Веб-панель", 
            command=self.open_web_panel,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Статус сервера
        status_frame = ttk.LabelFrame(self.root, text="Статус", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Сервер: Остановлен", 
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.status_dot = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=5)
        self.draw_status_dot(False)
        
        # Статистика
        stats_frame = ttk.LabelFrame(self.root, text="Статистика", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X)
        
        self.stats_labels = {}
        stats_data = [
            ("Всего напечатано:", "total"),
            ("Успешных:", "success"),
            ("Ошибок:", "failed"),
            ("Сегодня:", "today")
        ]
        
        for i, (label, key) in enumerate(stats_data):
            frame = ttk.Frame(stats_inner)
            frame.grid(row=i // 2, column=i % 2, padx=20, pady=5, sticky=tk.W)
            ttk.Label(frame, text=label, font=("Arial", 10)).pack(side=tk.LEFT)
            self.stats_labels[key] = ttk.Label(frame, text="0", font=("Arial", 10, "bold"))
            self.stats_labels[key].pack(side=tk.LEFT, padx=5)
        
        # История печати
        history_frame = ttk.LabelFrame(self.root, text="Последние печати", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица истории
        columns = ("Время", "Ячейка", "Статус")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка обновления истории
        ttk.Button(
            history_frame, 
            text="🔄 Обновить", 
            command=self.update_history
        ).pack(pady=5)
        
        # Нижняя панель с логами
        log_frame = ttk.LabelFrame(self.root, text="Логи", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def draw_status_dot(self, is_running):
        """Отрисовка индикатора статуса"""
        self.status_dot.delete("all")
        color = "#4CAF50" if is_running else "#f44336"
        self.status_dot.create_oval(5, 5, 15, 15, fill=color, outline="")
    
    def toggle_server(self):
        """Запуск/остановка сервера"""
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Запуск сервера в отдельном потоке"""
        try:
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            self.server_running = True
            self.start_btn.config(text="⏸ Остановить сервер")
            self.log("Сервер запущен на http://localhost:5001")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить сервер:\n{e}")
            self.log(f"Ошибка запуска: {e}", error=True)
    
    def stop_server(self):
        """Остановка сервера"""
        # В реальной реализации нужно корректно останавливать Flask сервер
        # Для упрощения просто меняем флаг
        self.server_running = False
        self.start_btn.config(text="▶ Запустить сервер")
        self.log("Сервер остановлен")
        messagebox.showinfo("Информация", "Сервер остановлен")
    
    def run_server(self):
        """Запуск Flask сервера"""
        try:
            # Запускаем сервер
            server.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
        except Exception as e:
            self.log(f"Ошибка сервера: {e}", error=True)
            self.server_running = False
    
    def update_status(self):
        """Обновление статуса и статистики"""
        if self.server_running:
            try:
                import requests
                response = requests.get("http://localhost:5001/status", timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    printer_status = "Подключен" if data.get('printer') == 'ok' else "Не подключен"
                    self.status_label.config(text=f"Сервер: Работает | Принтер: {printer_status}")
                    self.draw_status_dot(True)
                    
                    # Обновляем статистику
                    stats_response = requests.get("http://localhost:5001/statistics", timeout=1)
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        from datetime import datetime
                        today = datetime.now().strftime('%Y-%m-%d')
                        
                        self.stats_labels['total'].config(text=str(stats.get('total_printed', 0)))
                        self.stats_labels['success'].config(text=str(stats.get('successful_prints', 0)))
                        self.stats_labels['failed'].config(text=str(stats.get('failed_prints', 0)))
                        self.stats_labels['today'].config(text=str(stats.get('prints_by_day', {}).get(today, 0)))
                    
                    # Обновляем историю
                    self.update_history()
                else:
                    self.status_label.config(text="Сервер: Ошибка подключения")
                    self.draw_status_dot(False)
            except Exception as e:
                self.status_label.config(text="Сервер: Ошибка")
                self.draw_status_dot(False)
        else:
            self.status_label.config(text="Сервер: Остановлен")
            self.draw_status_dot(False)
        
        # Планируем следующее обновление
        self.update_id = self.root.after(2000, self.update_status)
    
    def update_history(self):
        """Обновление истории печати"""
        if not self.server_running:
            return
        
        try:
            import requests
            response = requests.get("http://localhost:5001/history?limit=20", timeout=1)
            if response.status_code == 200:
                data = response.json()
                history = data.get('history', [])
                
                # Очищаем текущие записи
                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)
                
                # Добавляем новые записи (в обратном порядке - новые сверху)
                for entry in reversed(history):
                    timestamp = entry.get('timestamp', '')[:19].replace('T', ' ')
                    cell_number = entry.get('cell_number', '')
                    status = "✓" if entry.get('success') else "✗"
                    status_color = "green" if entry.get('success') else "red"
                    
                    item = self.history_tree.insert("", 0, values=(timestamp, cell_number, status))
                    # Можно добавить цветовую маркировку, но tkinter ограничен
        except Exception as e:
            pass  # Игнорируем ошибки при обновлении
    
    def open_printer_settings(self):
        """Открытие веб-интерфейса настроек"""
        webbrowser.open("http://localhost:5001/settings")
    
    def install_extension(self):
        """Показ инструкции по установке расширения"""
        extension_path = Path(__file__).parent / "extension"
        
        if not extension_path.exists():
            messagebox.showerror("Ошибка", "Папка 'extension' не найдена!")
            return
        
        instruction = f"""УСТАНОВКА РАСШИРЕНИЯ БРАУЗЕРА

1. Откройте браузер (Chrome, Яндекс.Браузер или Edge)

2. Перейдите на страницу расширений:
   Chrome: chrome://extensions/
   Яндекс.Браузер: browser://extensions/
   Edge: edge://extensions/

3. Включите "Режим разработчика" (переключатель справа вверху)

4. Нажмите "Загрузить распакованное расширение"

5. Выберите папку:
   {extension_path}

6. Готово! Расширение установлено.

Папка расширения будет открыта в проводнике."""
        
        messagebox.showinfo("Установка расширения", instruction)
        
        # Открываем папку расширения
        if sys.platform == "win32":
            os.startfile(extension_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(extension_path)])
        else:
            subprocess.run(["xdg-open", str(extension_path)])
        
        # Открываем страницы расширений
        webbrowser.open("chrome://extensions/")
        webbrowser.open("browser://extensions/")
        webbrowser.open("edge://extensions/")
    
    def open_web_panel(self):
        """Открытие веб-панели управления"""
        webbrowser.open("http://localhost:5001/")
    
    def load_config(self):
        """Загрузка конфигурации"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.log("Конфигурация загружена")
            except Exception as e:
                self.log(f"Ошибка загрузки config.json: {e}", error=True)
    
    def log(self, message, error=False):
        """Добавление сообщения в лог"""
        self.log_text.config(state=tk.NORMAL)
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "[ERROR]" if error else "[INFO]"
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.server_running:
            if messagebox.askokcancel("Выход", "Сервер все еще работает. Остановить и выйти?"):
                self.stop_server()
                if self.update_id:
                    self.root.after_cancel(self.update_id)
                self.root.destroy()
        else:
            if self.update_id:
                self.root.after_cancel(self.update_id)
            self.root.destroy()


def main():
    root = tk.Tk()
    app = PrintServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

