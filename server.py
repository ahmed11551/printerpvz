#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервер для печати номеров ячеек на термопринтер
Поддерживает принтеры с протоколом ESC/POS
"""

import sys
import json
import os
import logging
import threading
import queue
from datetime import datetime
from collections import defaultdict
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import serial
import serial.tools.list_ports
from escpos.printer import Serial as EscPosSerial, Usb as EscPosUsb, Network as EscPosNetwork
from escpos.exceptions import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Разрешаем CORS для браузерного расширения

# Настройка логирования в файл
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'print_server_{datetime.now().strftime("%Y%m%d")}.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# История печати
HISTORY_FILE = 'print_history.json'
PRINT_HISTORY = []
MAX_HISTORY_ITEMS = 1000

# Статистика
STATISTICS = {
    'total_printed': 0,
    'successful_prints': 0,
    'failed_prints': 0,
    'prints_by_day': defaultdict(int),
    'last_print_time': None
}

# Очередь печати
print_queue = queue.Queue()
print_lock = threading.Lock()
print_worker_running = False

# Конфигурация принтера
PRINTER_CONFIG = {
    'type': 'serial',  # 'serial', 'usb', 'network'
    'serial_port': 'COM3',  # Windows: COM3, Linux/Mac: /dev/ttyUSB0 или /dev/tty.usbserial
    'serial_baudrate': 9600,
    'network_host': '192.168.1.100',
    'network_port': 9100,
    'width': 58,  # Ширина этикетки в мм (58мм - стандартная ширина)
    # Настройки печати (по умолчанию, можно переопределить в config.json)
    'printer_settings': {
        'width_mm': 58,
        'label_height_mm': 40,
        'font_size': 'large',
        'text_scale': {'width': 2, 'height': 2},
        'bold': True,
        'align': 'center',
        'print_qr': True,
        'qr_size': 8,
        'cut_after_print': True,
        'add_spacing': True
    },
    'label_template': {
        'header_text': 'ЯЧЕЙКА',
        'cell_number_scale': 2,
        'qr_below_text': True,
        'spacing_lines': 2
    }
}

printer_instance = None

def load_history():
    """Загрузка истории печати из файла"""
    global PRINT_HISTORY
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                PRINT_HISTORY = json.load(f)
                # Ограничиваем количество записей
                if len(PRINT_HISTORY) > MAX_HISTORY_ITEMS:
                    PRINT_HISTORY = PRINT_HISTORY[-MAX_HISTORY_ITEMS:]
        except Exception as e:
            logger.error(f"Ошибка загрузки истории: {e}")
            PRINT_HISTORY = []

def save_history():
    """Сохранение истории печати в файл"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(PRINT_HISTORY[-MAX_HISTORY_ITEMS:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения истории: {e}")

def add_to_history(cell_number, success=True, error=None):
    """Добавление записи в историю"""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'cell_number': cell_number,
        'success': success,
        'error': str(error) if error else None
    }
    PRINT_HISTORY.append(entry)
    if len(PRINT_HISTORY) > MAX_HISTORY_ITEMS:
        PRINT_HISTORY.pop(0)
    save_history()
    
    # Обновление статистики
    STATISTICS['total_printed'] += 1
    if success:
        STATISTICS['successful_prints'] += 1
    else:
        STATISTICS['failed_prints'] += 1
    STATISTICS['prints_by_day'][datetime.now().strftime('%Y-%m-%d')] += 1
    STATISTICS['last_print_time'] = datetime.now().isoformat()

def scan_serial_ports():
    """Автоматическое сканирование доступных COM-портов"""
    ports = []
    try:
        # Windows
        if sys.platform.startswith('win'):
            available_ports = serial.tools.list_ports.comports()
            for port in available_ports:
                ports.append({
                    'port': port.device,
                    'description': port.description,
                    'hardware_id': port.hwid
                })
        # macOS
        elif sys.platform == 'darwin':
            import glob
            usb_ports = glob.glob('/dev/tty.usbserial*') + glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/cu.*')
            for port_path in usb_ports:
                ports.append({
                    'port': port_path,
                    'description': 'USB Serial Port',
                    'hardware_id': None
                })
        # Linux
        else:
            import glob
            usb_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
            for port_path in usb_ports:
                ports.append({
                    'port': port_path,
                    'description': 'USB Serial Port',
                    'hardware_id': None
                })
    except Exception as e:
        logger.error(f"Ошибка сканирования портов: {e}")
    
    return ports

def load_config():
    """Загрузка конфигурации из файла"""
    global PRINTER_CONFIG
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Глубокая замена вложенных словарей
                for key, value in user_config.items():
                    if key in PRINTER_CONFIG and isinstance(PRINTER_CONFIG[key], dict) and isinstance(value, dict):
                        PRINTER_CONFIG[key].update(value)
                    else:
                        PRINTER_CONFIG[key] = value
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            logger.info("Используются настройки по умолчанию")

def init_printer():
    """Инициализация принтера"""
    global printer_instance
    
    # Закрываем предыдущее подключение если есть
    if printer_instance:
        try:
            printer_instance.close()
        except:
            pass
        printer_instance = None
    
    try:
        if PRINTER_CONFIG['type'] == 'serial':
            serial_port = PRINTER_CONFIG.get('serial_port', '')
            if not serial_port or serial_port.strip() == '':
                raise ValueError("Порт принтера не указан в config.json. Укажите правильный COM-порт (например, COM3 для Windows или /dev/tty.usbserial для Mac/Linux)")
            printer_instance = EscPosSerial(
                devfile=serial_port,
                baudrate=PRINTER_CONFIG['serial_baudrate'],
                timeout=3.0
            )
        elif PRINTER_CONFIG['type'] == 'usb':
            # Для USB принтеров нужны vendor_id и product_id
            vendor_id = PRINTER_CONFIG.get('vendor_id', 0x04f9)
            product_id = PRINTER_CONFIG.get('product_id', 0x2042)
            printer_instance = EscPosUsb(idVendor=vendor_id, idProduct=product_id)
        elif PRINTER_CONFIG['type'] == 'network':
            printer_instance = EscPosNetwork(
                host=PRINTER_CONFIG['network_host'],
                port=PRINTER_CONFIG['network_port'],
                timeout=3
            )
        else:
            raise ValueError(f"Неизвестный тип принтера: {PRINTER_CONFIG['type']}")
        
        logger.info(f"Принтер инициализирован: {PRINTER_CONFIG['type']}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации принтера: {e}")
        logger.info("Проверьте настройки в config.json")
        printer_instance = None
        return False

def print_cell_label(cell_number, retry_count=0, max_retries=3):
    """Печать этикетки с номером ячейки"""
    global printer_instance
    
    logger.info(f"Попытка печати ячейки: {cell_number} (попытка {retry_count + 1}/{max_retries + 1})")
    
    # Попытка инициализации если принтер не подключен
    if not printer_instance:
        if not init_printer():
            error_msg = "Принтер не инициализирован. Проверьте подключение и настройки в config.json"
            logger.error(error_msg)
            if retry_count < max_retries:
                # Добавляем в очередь для повтора
                print_queue.put({'cell_number': cell_number, 'retry_count': retry_count + 1, 'max_retries': max_retries})
                raise Exception(f"{error_msg} (будет повторена попытка)")
            raise Exception(error_msg)
    
    try:
        # Получаем настройки печати
        settings = PRINTER_CONFIG.get('printer_settings', {})
        template = PRINTER_CONFIG.get('label_template', {})
        
        # Настройки масштабирования текста
        text_scale = settings.get('text_scale', {'width': 2, 'height': 2})
        text_width = text_scale.get('width', 2)
        text_height = text_scale.get('height', 2)
        
        # Настройка принтера
        printer_instance.set(
            align=settings.get('align', 'center'),
            font='a',
            width=text_width,
            height=text_height,
            bold=settings.get('bold', True)
        )
        
        # Отступы сверху
        spacing = template.get('spacing_lines', 2)
        if settings.get('add_spacing', True):
            printer_instance.text("\n" * spacing)
        
        # Заголовок (если указан)
        header_text = template.get('header_text', 'ЯЧЕЙКА')
        if header_text:
            printer_instance.text(f"{header_text}\n")
            printer_instance.text("\n")
        
        # Номер ячейки (крупным шрифтом)
        cell_scale = template.get('cell_number_scale', 2)
        printer_instance.set(
            align=settings.get('align', 'center'),
            width=cell_scale,
            height=cell_scale,
            bold=True
        )
        printer_instance.text(f"{cell_number}\n")
        
        # Отступ перед QR-кодом
        if settings.get('add_spacing', True):
            printer_instance.text("\n")
        
        # QR-код (если включен)
        if settings.get('print_qr', True):
            printer_instance.set(align=settings.get('align', 'center'))
            try:
                qr_size = settings.get('qr_size', 8)
                printer_instance.qr(cell_number, size=qr_size, ec=0)
            except Exception as qr_error:
                # Если QR-код не поддерживается, пропускаем
                print(f"QR-код не напечатан (возможно не поддерживается): {qr_error}")
                pass
        
        # Отступы снизу
        if settings.get('add_spacing', True):
            printer_instance.text("\n" * spacing)
        
        # Отрезание этикетки
        if settings.get('cut_after_print', True):
            printer_instance.cut()
        
        logger.info(f"Ячейка {cell_number} успешно напечатана")
        add_to_history(cell_number, success=True)
        return True
        
    except (ConnectionError, OSError, serial.SerialException) as e:
        logger.error(f"Ошибка подключения к принтеру: {e}")
        printer_instance = None  # Сбрасываем подключение
        error_msg = f"Ошибка подключения к принтеру: {e}. Проверьте подключение принтера."
        
        # Добавляем в очередь для повтора, если не превышен лимит
        if retry_count < max_retries:
            print_queue.put({'cell_number': cell_number, 'retry_count': retry_count + 1, 'max_retries': max_retries})
            logger.info(f"Задача добавлена в очередь для повтора (попытка {retry_count + 1}/{max_retries})")
            raise Exception(f"{error_msg} (будет повторена попытка)")
        
        add_to_history(cell_number, success=False, error=error_msg)
        raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Ошибка печати: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        if retry_count < max_retries:
            print_queue.put({'cell_number': cell_number, 'retry_count': retry_count + 1, 'max_retries': max_retries})
            logger.info(f"Задача добавлена в очередь для повтора (попытка {retry_count + 1}/{max_retries})")
        
        add_to_history(cell_number, success=False, error=str(e))
        raise

def print_worker():
    """Фоновый процесс для обработки очереди печати"""
    global print_worker_running
    logger.info("Запущен процесс обработки очереди печати")
    
    while print_worker_running:
        try:
            # Получаем задачу из очереди (таймаут 1 секунда)
            try:
                task = print_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            cell_number = task['cell_number']
            retry_count = task.get('retry_count', 0)
            max_retries = task.get('max_retries', 3)
            
            logger.info(f"Обработка задачи из очереди: {cell_number} (попытка {retry_count + 1})")
            
            try:
                with print_lock:
                    print_cell_label(cell_number, retry_count=retry_count, max_retries=max_retries)
                logger.info(f"Задача выполнена успешно: {cell_number}")
            except Exception as e:
                logger.error(f"Ошибка при выполнении задачи {cell_number}: {e}")
                # Если превышен лимит попыток, не добавляем обратно
                if retry_count >= max_retries:
                    logger.error(f"Превышен лимит попыток для ячейки {cell_number}")
            
            print_queue.task_done()
        except Exception as e:
            logger.error(f"Ошибка в print_worker: {e}")
            import traceback
            logger.error(traceback.format_exc())

@app.before_request
def log_request():
    """Логирование всех запросов"""
    logger.info(f"[{request.method}] {request.path} - {request.remote_addr}")
    if request.path not in ['/', '/status', '/print', '/test', '/favicon.ico', '/history', '/statistics', '/ports', '/config', '/settings']:
        logger.warning(f"Неизвестный путь: {request.path}")

@app.route('/print', methods=['POST', 'OPTIONS'])
def print_endpoint():
    """API endpoint для печати"""
    print(f"[{request.method}] /print - Origin: {request.headers.get('Origin', 'N/A')}")
    
    if request.method == 'OPTIONS':
        # CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Тело запроса пустое'}), 400
            
        cell_number = data.get('cellNumber')
        
        if not cell_number:
            return jsonify({'error': 'Номер ячейки не указан'}), 400
        
        # Пытаемся сразу напечатать
        try:
            with print_lock:
                print_cell_label(cell_number)
            return jsonify({
                'success': True,
                'message': f'Ячейка {cell_number} отправлена на печать'
            })
        except Exception as e:
            # Если не получилось, добавляем в очередь
            print_queue.put({'cell_number': cell_number, 'retry_count': 0, 'max_retries': 3})
            logger.info(f"Задача добавлена в очередь: {cell_number}")
            return jsonify({
                'success': True,
                'message': f'Ячейка {cell_number} добавлена в очередь печати'
            })
        
    except Exception as e:
        logger.error(f"Ошибка в print_endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history/page', methods=['GET'])
def history_page():
    """Веб-страница истории печати"""
    limit = request.args.get('limit', type=int, default=100)
    history_data = PRINT_HISTORY[-limit:]
    history_data.reverse()  # Новые сначала
    
    history_html = ''.join([
        f'''
        <tr>
            <td>{entry['timestamp']}</td>
            <td><strong>{entry['cell_number']}</strong></td>
            <td style="color: {'green' if entry['success'] else 'red'}">
                {'✓ Успешно' if entry['success'] else '✗ Ошибка'}
            </td>
            <td>{entry.get('error', '') if not entry['success'] else '-'}</td>
        </tr>
        ''' for entry in history_data
    ])
    
    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>История печати</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 20px auto; padding: 20px; }}
            .link {{ color: #007bff; text-decoration: none; margin: 10px 0; display: inline-block; }}
            .link:hover {{ text-decoration: underline; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; font-weight: bold; }}
            tr:hover {{ background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>История печати</h1>
        <a href="/" class="link">← Вернуться на главную</a>
        <p>Всего записей: {len(PRINT_HISTORY)}</p>
        <table>
            <tr>
                <th>Время</th>
                <th>Номер ячейки</th>
                <th>Статус</th>
                <th>Ошибка</th>
            </tr>
            {history_html if history_html else '<tr><td colspan="4" style="text-align:center;">История пуста</td></tr>'}
        </table>
    </body>
    </html>
    '''

@app.route('/', methods=['GET'])
def index():
    """Главная страница сервера"""
    printer_ok = printer_instance is not None
    if not printer_ok:
        printer_ok = init_printer()
    
    queue_size = print_queue.qsize()
    
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Сервер печати ячеек ПВЗ</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .status {{ padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .ok {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            h1 {{ color: #333; }}
            .endpoint {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; }}
            code {{ background: #e9ecef; padding: 2px 5px; border-radius: 3px; }}
            .link {{ color: #007bff; text-decoration: none; margin: 10px 10px 10px 0; display: inline-block; }}
            .link:hover {{ text-decoration: underline; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
            .stat-label {{ color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <h1>Сервер печати ячеек ПВЗ</h1>
        <a href="/settings" class="link">⚙️ Настройки</a>
        <a href="/history/page" class="link">📋 История</a>
        <a href="/statistics" class="link">📊 Статистика</a>
        
        <div class="status {'ok' if printer_ok else 'error'}">
            <strong>Статус сервера:</strong> Работает [OK]<br>
            <strong>Статус принтера:</strong> {'Подключен [OK]' if printer_ok else 'Не подключен [ERROR]'}<br>
            <strong>Задач в очереди:</strong> {queue_size}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{STATISTICS['total_printed']}</div>
                <div class="stat-label">Всего напечатано</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{STATISTICS['successful_prints']}</div>
                <div class="stat-label">Успешных</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{STATISTICS['failed_prints']}</div>
                <div class="stat-label">Ошибок</div>
            </div>
        </div>
        
        <h2>Доступные API endpoints:</h2>
        <div class="endpoint">
            <strong>GET /status</strong> - Проверка статуса<br>
            <strong>GET /history</strong> - История печати<br>
            <strong>GET /statistics</strong> - Статистика<br>
            <strong>GET /ports</strong> - Список доступных портов<br>
            <strong>GET /settings</strong> - Веб-интерфейс настроек<br>
            <strong>POST /print</strong> - Печать ячейки<br>
            <strong>POST /test</strong> - Тестовая печать<br>
            <strong>GET /config</strong> - Текущая конфигурация<br>
            <strong>POST /config</strong> - Обновление конфигурации
        </div>
        <p><small>Версия 2.0.0</small></p>
    </body>
    </html>
    """, 200

@app.route('/status', methods=['GET'])
def status_endpoint():
    """Проверка статуса сервера и принтера"""
    printer_ok = printer_instance is not None
    
    if not printer_ok:
        printer_ok = init_printer()
    
    return jsonify({
        'server': 'ok',
        'printer': 'ok' if printer_ok else 'error',
        'queue_size': print_queue.qsize(),
        'config': {
            'type': PRINTER_CONFIG['type'],
            'port': PRINTER_CONFIG.get('serial_port') or PRINTER_CONFIG.get('network_host', 'N/A')
        }
    })

@app.route('/history', methods=['GET'])
def history_endpoint():
    """Получение истории печати"""
    limit = request.args.get('limit', type=int, default=100)
    return jsonify({
        'history': PRINT_HISTORY[-limit:],
        'total': len(PRINT_HISTORY)
    })

@app.route('/statistics', methods=['GET'])
def statistics_endpoint():
    """Получение статистики использования"""
    stats = STATISTICS.copy()
    # Преобразуем defaultdict в обычный dict для JSON
    stats['prints_by_day'] = dict(stats['prints_by_day'])
    return jsonify(stats)

@app.route('/ports', methods=['GET'])
def ports_endpoint():
    """Получение списка доступных COM-портов"""
    ports = scan_serial_ports()
    return jsonify({'ports': ports})

@app.route('/config', methods=['GET'])
def get_config():
    """Получение текущей конфигурации"""
    return jsonify(PRINTER_CONFIG)

@app.route('/config', methods=['POST'])
def update_config():
    """Обновление конфигурации принтера"""
    global PRINTER_CONFIG
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Тело запроса пустое'}), 400
        
        # Обновляем конфигурацию
        for key, value in data.items():
            if key in PRINTER_CONFIG and isinstance(PRINTER_CONFIG[key], dict) and isinstance(value, dict):
                PRINTER_CONFIG[key].update(value)
            else:
                PRINTER_CONFIG[key] = value
        
        # Сохраняем в файл
        config_file = 'config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(PRINTER_CONFIG, f, ensure_ascii=False, indent=2)
        
        # Переинициализируем принтер
        init_printer()
        
        logger.info("Конфигурация обновлена")
        return jsonify({'success': True, 'message': 'Конфигурация обновлена', 'config': PRINTER_CONFIG})
        
    except Exception as e:
        logger.error(f"Ошибка обновления конфигурации: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Тестовая печать"""
    try:
        with print_lock:
            print_cell_label('TEST-1')
        return jsonify({'success': True, 'message': 'Тестовая печать выполнена'})
    except Exception as e:
        logger.error(f"Ошибка тестовой печати: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/status', '/print', '/test', '/config', '/history', '/statistics', '/ports', '/settings']
    }), 404

if __name__ == '__main__':
    logger.info("Загрузка конфигурации...")
    load_config()
    
    logger.info("Загрузка истории...")
    load_history()
    
    logger.info("Инициализация принтера...")
    init_printer()
    
    # Запуск фонового процесса обработки очереди
    print_worker_running = True
    worker_thread = threading.Thread(target=print_worker, daemon=True)
    worker_thread.start()
    logger.info("Запущен процесс обработки очереди печати")
    
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Запуск сервера на http://localhost:{port}")
    logger.info("Доступные endpoints: /, /status, /print, /test, /config, /history, /statistics, /ports, /settings")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("Остановка сервера...")
        print_worker_running = False
        worker_thread.join(timeout=2)
        logger.info("Сервер остановлен")

