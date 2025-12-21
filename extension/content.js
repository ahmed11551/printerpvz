// Content script для перехвата номеров ячеек

(function() {
    'use strict';
    
    const CONFIG = {
        ozon: {
            // Расширенный список селекторов для Ozon
            selectors: [
                // Специфичные для Ozon
                '[class*="cell"]',
                '[class*="ячейк"]',
                '[class*="Cell"]',
                '[class*="Ячейк"]',
                '[data-cell]',
                '[data-cell-number]',
                '[data-cell-id]',
                '[id*="cell"]',
                '[id*="ячейк"]',
                '[id*="Cell"]',
                // Input поля
                'input[value*="-"]',
                'input[class*="cell"]',
                // Конкретные классы
                '.cell-number',
                '.cell-id',
                '.cell-code',
                '[class*="cell-number"]',
                '[class*="cell-id"]',
                '[class*="cell-code"]',
                // Toast уведомления и модалки
                '[class*="notification"]',
                '[class*="toast"]',
                '[class*="message"]',
                '[class*="alert"]',
                // Таблицы и списки
                'td[class*="cell"]',
                'span[class*="cell"]',
                'div[class*="cell"]'
            ],
            // Расширенные паттерны для разных форматов ячеек
            patterns: [
                // Стандартные форматы с дефисом
                // A1-1, B2-3, Z99-99 (буква-цифра-цифра)
                /\b([A-Za-z]\d+[-]\d+)\b/,
                // AA1-1, AB2-3 (двухбуквенные)
                /\b([A-Za-z]{2}\d+[-]\d+)\b/,
                // 1-1, 12-5, 99-99 (цифра-цифра)
                /\b(\d{1,3}[-]\d{1,3})\b/,
                // A-1, B-5 (буква-цифра)
                /\b([A-Za-z][-]\d+)\b/,
                
                // Форматы с точкой
                // A1.1, B2.3 (буква-цифра.цифра)
                /\b([A-Za-z]\d+[\.]\d+)\b/,
                // AA1.1 (двухбуквенные с точкой)
                /\b([A-Za-z]{2}\d+[\.]\d+)\b/,
                // 1.1, 12.5 (цифра.цифра)
                /\b(\d{1,3}[\.]\d{1,3})\b/,
                
                // Форматы с подчеркиванием
                // A1_1, B2_3 (буква-цифра_цифра)
                /\b([A-Za-z]\d+[_]\d+)\b/,
                // AA1_1 (двухбуквенные с подчеркиванием)
                /\b([A-Za-z]{2}\d+[_]\d+)\b/,
                // 1_1, 12_5 (цифра_цифра)
                /\b(\d{1,3}[_]\d{1,3})\b/,
                
                // Форматы со слэшем
                // A1/1, B2/3
                /\b([A-Za-z]\d+[\/]\d+)\b/,
                // AA1/1
                /\b([A-Za-z]{2}\d+[\/]\d+)\b/,
                // 1/1, 12/5
                /\b(\d{1,3}[\/]\d{1,3})\b/,
                
                // Форматы без разделителя (A11, B23, но не простые числа)
                /\b([A-Za-z]\d{2,4})\b/,
                /\b([A-Za-z]{2}\d{2,4})\b/,
                
                // С текстом "ячейка: A1-1", "Ячейка: 1-1"
                /\b[яЯ]чейк[аи]?[:\s]*([A-Za-z]?\d+[-\._\/]?\d+)\b/i,
                // С текстом "122 ячейка", "ячейка 122" - простые числа (если встречаются в контексте "ячейка")
                /\b(\d{1,4})\s+[яЯ]чейк[аи]?\b/i,
                /\b[яЯ]чейк[аи]?\s+(\d{1,4})\b/i,
                // В скобках (A1-1), [1-1], (A1.1)
                /[\(\[\s]*([A-Za-z]?\d+[-\._\/]\d+)[\)\]\s]*/,
                // С префиксом Cell: или ячейка
                /(?:[яЯ]чейк[аи]?|cell)[:\s]*([A-Za-z]?\d+[-\._\/]\d+)/i,
                // С пробелами: "A 1 - 1", "B 2 . 3"
                /\b([A-Za-z])\s*(\d+)\s*[-\._\/]\s*(\d+)\b/,
            ],
            // Паттерны для исключения (ложные срабатывания)
            excludePatterns: [
                /\d+[-]\d+[-]\d+/,  // Дата: 2024-12-17
                /\d+:\d+/,           // Время: 12:30
                /\d+\.\d+/,          // IP адрес или версия: 192.168.1.1
                /https?:\/\//,       // URL
                /@\w+/,              // Email или упоминания
                /\d{4,}/             // Длинные числа (ID заказов, телефоны)
            ]
        },
        wildberries: {
            // Расширенный список селекторов для Wildberries
            selectors: [
                '[class*="cell"]',
                '[class*="ячейк"]',
                '[class*="Cell"]',
                '[class*="Ячейк"]',
                '[data-cell]',
                '[data-cell-number]',
                '[data-cell-id]',
                '[id*="cell"]',
                '[id*="ячейк"]',
                'input[value*="-"]',
                'input[class*="cell"]',
                '.cell-number',
                '.cell-id',
                '.cell-code',
                '[class*="cell-number"]',
                '[class*="cell-id"]',
                '[class*="notification"]',
                '[class*="toast"]',
                '[class*="message"]',
                'td[class*="cell"]',
                'span[class*="cell"]',
                'div[class*="cell"]'
            ],
            patterns: [
                // Стандартные форматы с дефисом
                /\b([A-Za-z]\d+[-]\d+)\b/,
                /\b([A-Za-z]{2}\d+[-]\d+)\b/,
                /\b(\d{1,3}[-]\d{1,3})\b/,
                /\b([A-Za-z][-]\d+)\b/,
                
                // Форматы с точкой
                /\b([A-Za-z]\d+[\.]\d+)\b/,
                /\b([A-Za-z]{2}\d+[\.]\d+)\b/,
                /\b(\d{1,3}[\.]\d{1,3})\b/,
                
                // Форматы с подчеркиванием
                /\b([A-Za-z]\d+[_]\d+)\b/,
                /\b([A-Za-z]{2}\d+[_]\d+)\b/,
                /\b(\d{1,3}[_]\d{1,3})\b/,
                
                // Форматы со слэшем
                /\b([A-Za-z]\d+[\/]\d+)\b/,
                /\b([A-Za-z]{2}\d+[\/]\d+)\b/,
                /\b(\d{1,3}[\/]\d{1,3})\b/,
                
                // Форматы без разделителя
                /\b([A-Za-z]\d{2,4})\b/,
                /\b([A-Za-z]{2}\d{2,4})\b/,
                
                // С текстом
                /\b[яЯ]чейк[аи]?[:\s]*([A-Za-z]?\d+[-\._\/]?\d+)\b/i,
                // С текстом "122 ячейка", "ячейка 122" - простые числа (если встречаются в контексте "ячейка")
                /\b(\d{1,4})\s+[яЯ]чейк[аи]?\b/i,
                /\b[яЯ]чейк[аи]?\s+(\d{1,4})\b/i,
                /[\(\[\s]*([A-Za-z]?\d+[-\._\/]\d+)[\)\]\s]*/,
                /(?:[яЯ]чейк[аи]?|cell)[:\s]*([A-Za-z]?\d+[-\._\/]\d+)/i,
                /\b([A-Za-z])\s*(\d+)\s*[-\._\/]\s*(\d+)\b/,
            ],
            excludePatterns: [
                /\d+[-]\d+[-]\d+/,  // Дата
                /\d+:\d+/,           // Время
                /\d+\.\d+/,          // IP адрес
                /https?:\/\//,       // URL
                /@\w+/,              // Email
                /\d{4,}/             // Длинные числа
            ]
        }
    };
    
    let lastPrintedCell = null;
    let observer = null;
    
    // Определяем тип платформы
    function getPlatform() {
        const hostname = window.location.hostname;
        if (hostname.includes('ozon.ru')) return 'ozon';
        if (hostname.includes('wildberries.ru')) return 'wildberries';
        return 'unknown';
    }
    
    // Валидация номера ячейки (исключение ложных срабатываний)
    function isValidCellNumber(cellNumber, text, platform, element = null) {
        if (!cellNumber) return false;
        
        // Проверка на исключающие паттерны
        const excludePatterns = CONFIG[platform]?.excludePatterns || CONFIG.ozon.excludePatterns;
        for (const excludePattern of excludePatterns) {
            if (excludePattern.test(text)) {
                // Если в тексте есть исключающий паттерн рядом с номером ячейки
                const context = text.substring(Math.max(0, text.indexOf(cellNumber) - 20), 
                                                Math.min(text.length, text.indexOf(cellNumber) + cellNumber.length + 20));
                if (excludePattern.test(context)) {
                    return false;
                }
            }
        }
        
        // Валидация формата: должна быть хотя бы одна цифра
        if (!/\d/.test(cellNumber)) {
            return false;
        }
        
        // Должен быть разделитель (дефис, точка, подчеркивание, слэш) ИЛИ буква+цифры
        // Проверяем наличие разделителя ИЛИ формат буква+цифры (минимум 2 цифры)
        const hasSeparator = /[-\._\/]/.test(cellNumber);
        const hasLetterAndDigits = /[A-Za-z]\d{2,}/.test(cellNumber);
        
        if (!hasSeparator && !hasLetterAndDigits) {
            return false;
        }
        
        // Не должны быть слишком длинными (больше 15 символов, учитывая пробелы)
        const cleanCell = cellNumber.replace(/\s+/g, '');
        if (cleanCell.length > 15) {
            return false;
        }
        
        // Разрешаем простые числа (1-9999) если:
        // 1. Они в контексте слова "ячейка", ИЛИ
        // 2. Они найдены в специальных элементах (input, элементы с классами ячеек)
        if (/^\d+$/.test(cleanCell)) {
            // Проверяем, что это не слишком длинное число (максимум 4 цифры для ячеек)
            if (cleanCell.length > 4 || parseInt(cleanCell) <= 0) {
                return false;
            }
            
            // Если элемент передан и это специальный элемент (input, textarea, select или элемент с классом cell)
            if (element) {
                const tagName = element.tagName;
                const className = element.className || '';
                const id = element.id || '';
                const hasCellMarker = /cell|ячейк/i.test(className + ' ' + id);
                
                // Если это input/textarea/select или элемент с маркером "cell", разрешаем простое число
                if (tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT' || hasCellMarker) {
                    return true;
                }
            }
            
            // Проверяем контекст слова "ячейка" в тексте
            const cellNumberMatch = text.match(new RegExp(`\\b${cellNumber.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i'));
            if (cellNumberMatch) {
                const contextStart = Math.max(0, cellNumberMatch.index - 30);
                const contextEnd = Math.min(text.length, cellNumberMatch.index + cellNumberMatch[0].length + 30);
                const context = text.substring(contextStart, contextEnd).toLowerCase();
                
                // Если есть слово "ячейка" рядом с числом, разрешаем
                if (/\bячейк[аиы]?\b/i.test(context)) {
                    return true; // Разрешаем простые числа в контексте "ячейка"
                }
            }
            
            return false; // Простые числа без контекста "ячейка" и не в специальных элементах не допускаются
        }
        
        // Не должно быть только букв
        if (/^[A-Za-z]+$/.test(cleanCell)) {
            return false;
        }
        
        // Исключаем даты (формат YYYY-MM-DD или DD-MM-YYYY)
        if (/^\d{4}[-\._\/]\d{1,2}[-\._\/]\d{1,2}$/.test(cleanCell) || 
            /^\d{1,2}[-\._\/]\d{1,2}[-\._\/]\d{4}$/.test(cleanCell)) {
            return false;
        }
        
        // Исключаем IP адреса (формат XXX.XXX.XXX.XXX)
        if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(cleanCell)) {
            return false;
        }
        
        return true;
    }
    
    // Поиск номера ячейки в тексте
    function findCellNumber(text, platform, element = null) {
        if (!text || text.length > 5000) return null; // Ограничение на длину текста
        
        // Сначала проверяем паттерны с контекстом "ячейка" для простых чисел (приоритет)
        const cellNumberWithContextPattern = /\b(\d{1,4})\s+[яЯ]чейк[аи]?\b|\b[яЯ]чейк[аи]?\s+(\d{1,4})\b/i;
        const contextMatch = text.match(cellNumberWithContextPattern);
        if (contextMatch) {
            const cellNum = (contextMatch[1] || contextMatch[2]).trim();
            if (cellNum && isValidCellNumber(cellNum, text, platform, element)) {
                return cellNum;
            }
        }
        
        const patterns = CONFIG[platform]?.patterns || CONFIG.ozon.patterns;
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                let cellNumber;
                // Обработка паттерна с пробелами (например, "A 1 - 1" - последний паттерн с 3 группами)
                // Последний паттерн: /\b([A-Za-z])\s*(\d+)\s*[-\._\/]\s*(\d+)\b/
                if (match.length === 4 && match[1] && match[2] && match[3]) {
                    // Извлекаем разделитель из исходного текста
                    const separatorMatch = match[0].match(/[-\._\/]/);
                    const separator = separatorMatch ? separatorMatch[0] : '-';
                    cellNumber = (match[1] + match[2] + separator + match[3]).trim();
                } else if (match.length >= 3 && match[1] && match[2]) {
                    // Обработка паттерна с двумя группами (например, "122 ячейка")
                    cellNumber = (match[1] || match[2]).trim();
                } else {
                    cellNumber = (match[1] || match[0]).trim();
                }
                
                // Убираем пробелы и нормализуем
                cellNumber = cellNumber.replace(/\s+/g, '');
                
                // Проверяем валидность
                if (isValidCellNumber(cellNumber, text, platform, element)) {
                    return cellNumber;
                }
            }
        }
        
        return null;
    }
    
    // Поиск ячейки в DOM
    function searchCellInDOM() {
        const platform = getPlatform();
        if (platform === 'unknown') return null;
        
        const selectors = CONFIG[platform].selectors;
        
        // Приоритетный поиск: сначала в видимых элементах с классами/атрибутами ячеек
        for (const selector of selectors) {
            try {
                const elements = document.querySelectorAll(selector);
                for (const el of elements) {
                    // Проверяем только видимые элементы (или input/textarea/select - они могут быть скрыты но содержать данные)
                    if (el.offsetParent === null && !el.hasAttribute('value') && 
                        el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA' && el.tagName !== 'SELECT') continue;
                    
                    // Получаем текст из разных источников
                    const text = el.textContent || el.value || el.innerText || 
                                el.getAttribute('value') || el.getAttribute('data-cell') ||
                                el.getAttribute('data-cell-number') || el.getAttribute('data-cell-id') ||
                                el.title || el.placeholder;
                    
                    const cellNumber = findCellNumber(text, platform, el);
                    if (cellNumber) {
                        console.log('Ячейка найдена через селектор:', selector, cellNumber);
                        return cellNumber;
                    }
                }
            } catch (e) {
                console.warn('Selector error:', selector, e);
            }
        }
        
        // Дополнительный поиск в элементах, которые могли появиться после сканирования
        // Ищем элементы с крупным текстом (обычно ячейки выделяются крупно)
        const largeTextElements = document.querySelectorAll('*');
        for (const el of largeTextElements) {
            const style = window.getComputedStyle(el);
            const fontSize = parseFloat(style.fontSize);
            // Если размер шрифта больше 20px, это может быть номер ячейки
            if (fontSize >= 20 && el.textContent && el.textContent.trim().length < 20) {
                const cellNumber = findCellNumber(el.textContent, platform, el);
                if (cellNumber) {
                    console.log('Ячейка найдена в крупном тексте:', cellNumber);
                    return cellNumber;
                }
            }
        }
        
        // Поиск в модальных окнах и уведомлениях (приоритетный)
        const modals = document.querySelectorAll('[role="dialog"], .modal, [class*="modal"], [class*="dialog"], [class*="notification"], [class*="toast"], [class*="alert"]');
        for (const modal of modals) {
            // Проверяем видимость
            const style = window.getComputedStyle(modal);
            if (style.display === 'none' || style.visibility === 'hidden') continue;
            
            const text = modal.textContent || modal.innerText;
            const cellNumber = findCellNumber(text, platform);
            if (cellNumber) {
                console.log('Ячейка найдена в модальном окне:', cellNumber);
                return cellNumber;
            }
        }
        
        // Поиск в input полях (часто там появляются ячейки)
        const inputs = document.querySelectorAll('input[type="text"], input[type="hidden"], input:not([type])');
        for (const input of inputs) {
            const value = input.value || input.getAttribute('value');
            if (value) {
                const cellNumber = findCellNumber(value, platform);
                if (cellNumber) {
                    console.log('Ячейка найдена в input:', cellNumber);
                    return cellNumber;
                }
            }
        }
        
        // Поиск в элементах с выделенным текстом или фокусом
        const focusedEl = document.activeElement;
        if (focusedEl && focusedEl !== document.body) {
            const text = focusedEl.textContent || focusedEl.value || focusedEl.innerText;
            const cellNumber = findCellNumber(text, platform);
            if (cellNumber) {
                console.log('Ячейка найдена в активном элементе:', cellNumber);
                return cellNumber;
            }
        }
        
        // Поиск по всему видимому документу (последний вариант, но только видимый текст)
        const bodyText = document.body.innerText || document.body.textContent;
        // Ограничиваем поиск первыми 5000 символами (обычно ячейка появляется в начале)
        const limitedText = bodyText.substring(0, 5000);
        const cellNumber = findCellNumber(limitedText, platform);
        if (cellNumber) {
            console.log('Ячейка найдена в основном тексте:', cellNumber);
        }
        return cellNumber;
    }
    
    // Отправка номера ячейки на печать
    async function sendToPrint(cellNumber) {
        if (!cellNumber || cellNumber === lastPrintedCell) {
            return;
        }
        
        lastPrintedCell = cellNumber;
        
        try {
            // Получаем настройки из storage
            const result = await chrome.storage.sync.get(['printEnabled', 'serverUrl']);
            const printEnabled = result.printEnabled !== false; // По умолчанию включено
            const serverUrl = result.serverUrl || 'http://localhost:5001';
            
            if (!printEnabled) {
                console.log('Печать отключена');
                return;
            }
            
            console.log('Отправка на печать:', cellNumber);
            
            const response = await fetch(`${serverUrl}/print`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cellNumber: cellNumber })
            });
            
            if (response.ok) {
                console.log('Ячейка успешно отправлена на печать:', cellNumber);
                showNotification(cellNumber, true);
            } else {
                console.error('Ошибка печати:', response.statusText);
                showNotification(cellNumber, false);
            }
        } catch (error) {
            console.error('Ошибка отправки на печать:', error);
            showNotification(cellNumber, false);
        }
    }
    
    // Показ уведомления
    function showNotification(cellNumber, success = true) {
        // Звуковое уведомление (опционально, только если разрешено браузером)
        if (success) {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.2);
            } catch (e) {
                // Игнорируем ошибки звука (могут быть ограничения браузера)
            }
        }
        
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${success ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-size: 14px;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = success 
            ? `Ячейка ${cellNumber} отправлена на печать`
            : `Ошибка печати ячейки ${cellNumber}`;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // Добавляем CSS анимации
    if (!document.getElementById('print-notification-styles')) {
        const style = document.createElement('style');
        style.id = 'print-notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Поиск ячейки в недавно измененных элементах (приоритет при сканировании)
    function searchCellInRecentChanges(mutations) {
        const platform = getPlatform();
        if (platform === 'unknown') return null;
        
        // Собираем все недавно добавленные/измененные элементы
        const changedElements = new Set();
        
        for (const mutation of mutations) {
            // Новые добавленные узлы
            if (mutation.addedNodes) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        changedElements.add(node);
                        // Также проверяем дочерние элементы
                        if (node.querySelectorAll) {
                            node.querySelectorAll('*').forEach(child => changedElements.add(child));
                        }
                    }
                });
            }
            
            // Измененные узлы
            if (mutation.target && mutation.target.nodeType === 1) {
                changedElements.add(mutation.target);
            }
        }
        
        // Приоритетный поиск в недавно измененных элементах
        for (const element of changedElements) {
            // Проверяем текст элемента
            const text = element.textContent || element.innerText || element.value;
            if (text) {
                const cellNumber = findCellNumber(text, platform, element);
                if (cellNumber) {
                    console.log('Ячейка найдена в недавно измененном элементе:', cellNumber, element);
                    return cellNumber;
                }
            }
            
            // Проверяем атрибуты
            const value = element.getAttribute('value') || element.getAttribute('data-cell') || 
                         element.getAttribute('data-cell-number') || element.getAttribute('data-cell-id');
            if (value) {
                const cellNumber = findCellNumber(value, platform, element);
                if (cellNumber) {
                    console.log('Ячейка найдена в атрибуте измененного элемента:', cellNumber, element);
                    return cellNumber;
                }
            }
        }
        
        return null;
    }
    
    // Мониторинг изменений DOM
    function startMonitoring() {
        if (observer) {
            observer.disconnect();
        }
        
        // MutationObserver для отслеживания изменений после сканирования
        observer = new MutationObserver((mutations) => {
            // Сначала проверяем недавно измененные элементы (быстрее и точнее)
            const cellNumber = searchCellInRecentChanges(mutations);
            if (cellNumber) {
                sendToPrint(cellNumber);
                return;
            }
            
            // Если не нашли в изменениях, делаем полный поиск
            const fullSearchCell = searchCellInDOM();
            if (fullSearchCell) {
                sendToPrint(fullSearchCell);
            }
        });
        
        // Отслеживаем все изменения в DOM (после сканирования данные появятся здесь)
        observer.observe(document.body, {
            childList: true,      // Добавление/удаление элементов
            subtree: true,        // Во всех вложенных элементах
            characterData: true,  // Изменения текста
            attributes: true,     // Изменения атрибутов (value, data-* и т.д.)
            attributeOldValue: false  // Не сохраняем старое значение для производительности
        });
        
        // Дополнительно отслеживаем изменения значений input полей (часто используется при сканировании)
        document.addEventListener('input', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                const value = e.target.value;
                if (value) {
                    const platform = getPlatform();
                    const cellNumber = findCellNumber(value, platform);
                    if (cellNumber) {
                        console.log('Ячейка найдена в input поле после ввода:', cellNumber);
                        sendToPrint(cellNumber);
                    }
                }
            }
        }, true); // Используем capture phase для перехвата всех событий
        
        // Отслеживаем изменения через события (на случай если MutationObserver пропустит)
        document.addEventListener('DOMContentLoaded', () => {
            const cellNumber = searchCellInDOM();
            if (cellNumber) {
                sendToPrint(cellNumber);
            }
        });
        
        // Периодическая проверка (резервный метод)
        setInterval(() => {
            const cellNumber = searchCellInDOM();
            if (cellNumber) {
                sendToPrint(cellNumber);
            }
        }, 2000);
        
        // Первоначальная проверка
        setTimeout(() => {
            const cellNumber = searchCellInDOM();
            if (cellNumber) {
                sendToPrint(cellNumber);
            }
        }, 1000);
    }
    
    // Перехват событий клавиатуры для ручного ввода
    document.addEventListener('keydown', (e) => {
        // Если нажата комбинация Ctrl+Enter после ввода номера ячейки
        if (e.ctrlKey && e.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
                const cellNumber = findCellNumber(activeElement.value, getPlatform());
                if (cellNumber) {
                    sendToPrint(cellNumber);
                }
            }
        }
    });
    
    // Запуск при загрузке страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startMonitoring);
    } else {
        startMonitoring();
    }
    
    console.log('Плагин печати ячеек активирован');
})();

