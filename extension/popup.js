// Popup script для настроек расширения

document.addEventListener('DOMContentLoaded', async () => {
    const printEnabledCheckbox = document.getElementById('printEnabled');
    const serverUrlInput = document.getElementById('serverUrl');
    const testCellInput = document.getElementById('testCell');
    const testPrintButton = document.getElementById('testPrint');
    const statusDiv = document.getElementById('status');
    const serverDot = document.getElementById('serverDot');
    const serverStatusText = document.getElementById('serverStatusText');
    const openSettingsBtn = document.getElementById('openSettings');
    const openHistoryBtn = document.getElementById('openHistory');
    const openDashboardBtn = document.getElementById('openDashboard');
    const todayCountEl = document.getElementById('todayCount');
    const totalCountEl = document.getElementById('totalCount');
    
    // Загрузка сохраненных настроек
    const result = await chrome.storage.sync.get(['printEnabled', 'serverUrl']);
    
    if (result.printEnabled !== undefined) {
        printEnabledCheckbox.checked = result.printEnabled;
    }
    
    if (result.serverUrl) {
        serverUrlInput.value = result.serverUrl;
    }
    
    // Проверка статуса сервера и статистики
    async function checkServerStatus() {
        const serverUrl = serverUrlInput.value || 'http://localhost:5001';
        try {
            const [statusResponse, statsResponse] = await Promise.all([
                fetch(`${serverUrl}/status`),
                fetch(`${serverUrl}/statistics`)
            ]);
            
            if (statusResponse.ok) {
                const statusData = await statusResponse.json();
                serverDot.className = 'status-dot ' + (statusData.printer === 'ok' ? 'printer-ok' : 'printer-error');
                const queueInfo = statusData.queue_size > 0 ? ` (Очередь: ${statusData.queue_size})` : '';
                serverStatusText.textContent = `Сервер: OK, Принтер: ${statusData.printer === 'ok' ? 'OK' : 'ERROR'}${queueInfo}`;
            } else {
                serverDot.className = 'status-dot offline';
                serverStatusText.textContent = 'Сервер недоступен';
            }
            
            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                const today = new Date().toISOString().split('T')[0];
                const todayCount = statsData.prints_by_day[today] || 0;
                todayCountEl.textContent = todayCount;
                totalCountEl.textContent = statsData.total_printed || 0;
            }
        } catch (error) {
            serverDot.className = 'status-dot offline';
            serverStatusText.textContent = 'Сервер недоступен';
        }
    }
    
    // Проверяем статус при загрузке и при изменении URL
    checkServerStatus();
    serverUrlInput.addEventListener('blur', checkServerStatus);
    
    // Автообновление статуса каждые 5 секунд
    setInterval(checkServerStatus, 5000);
    
    // Быстрые ссылки
    openSettingsBtn.addEventListener('click', () => {
        const serverUrl = serverUrlInput.value || 'http://localhost:5001';
        chrome.tabs.create({ url: `${serverUrl}/settings` });
    });
    
    openHistoryBtn.addEventListener('click', () => {
        const serverUrl = serverUrlInput.value || 'http://localhost:5001';
        chrome.tabs.create({ url: `${serverUrl}/history/page` });
    });
    
    openDashboardBtn.addEventListener('click', () => {
        const serverUrl = serverUrlInput.value || 'http://localhost:5001';
        chrome.tabs.create({ url: serverUrl });
    });
    
    // Сохранение настроек при изменении
    printEnabledCheckbox.addEventListener('change', async () => {
        await chrome.storage.sync.set({ printEnabled: printEnabledCheckbox.checked });
        showStatus('Настройки сохранены', 'success');
    });
    
    serverUrlInput.addEventListener('blur', async () => {
        await chrome.storage.sync.set({ serverUrl: serverUrlInput.value });
        showStatus('Настройки сохранены', 'success');
    });
    
    // Тестовая печать
    testPrintButton.addEventListener('click', async () => {
        const cellNumber = testCellInput.value.trim();
        if (!cellNumber) {
            showStatus('Введите номер ячейки', 'error');
            return;
        }
        
        testPrintButton.disabled = true;
        testPrintButton.textContent = 'Печать...';
        
        try {
            const serverUrl = serverUrlInput.value || 'http://localhost:5001';
            const response = await fetch(`${serverUrl}/print`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cellNumber: cellNumber })
            });
            
            if (response.ok) {
                showStatus(`Ячейка ${cellNumber} отправлена на печать`, 'success');
            } else {
                const errorText = await response.text();
                showStatus(`Ошибка: ${errorText}`, 'error');
            }
        } catch (error) {
            showStatus(`Ошибка подключения: ${error.message}`, 'error');
        } finally {
            testPrintButton.disabled = false;
            testPrintButton.textContent = 'Печать тестовой ячейки';
        }
    });
    
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = '';
        }, 3000);
    }
});

