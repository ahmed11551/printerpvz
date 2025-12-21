// Background service worker

chrome.runtime.onInstalled.addListener(() => {
    console.log('Расширение "Печать ячеек ПВЗ" установлено');
    
    // Установка значений по умолчанию
    chrome.storage.sync.set({
        printEnabled: true,
        serverUrl: 'http://localhost:5001'
    });
});

