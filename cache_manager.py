"""
Модуль управления кэшем для сканера API ключей
"""

import json
import os
from datetime import datetime
from typing import Set, Dict, List, Any
from pathlib import Path


class CacheManager:
    """Менеджер кэша для хранения обработанных файлов и протестированных ключей"""
    
    def __init__(self, cache_file: str = 'scanner_cache.json'):
        """
        Инициализация менеджера кэша
        
        Args:
            cache_file: Путь к файлу кэша
        """
        self.cache_file = cache_file
        self.processed_files: Set[str] = set()
        self.tested_keys: Set[str] = set()
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Загружает кэш из файла"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.processed_files = set(cache_data.get('processed_files', []))
                    self.tested_keys = set(cache_data.get('tested_keys', []))
                    
                print(f"📂 Загружен кэш: {len(self.processed_files)} файлов, {len(self.tested_keys)} ключей")
            else:
                print("📂 Кэш не найден, начинаем с чистого листа")
                
        except Exception as e:
            print(f"⚠️ Ошибка загрузки кэша: {e}")
            self.processed_files = set()
            self.tested_keys = set()
    
    def save_cache(self) -> None:
        """Сохраняет кэш в файл"""
        try:
            cache_data = {
                'processed_files': list(self.processed_files),
                'tested_keys': list(self.tested_keys),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Ошибка сохранения кэша: {e}")
    
    def clear_cache(self) -> None:
        """Очищает кэш"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            
            self.processed_files = set()
            self.tested_keys = set()
            print("🗑️ Кэш очищен")
            
        except Exception as e:
            print(f"⚠️ Ошибка очистки кэша: {e}")
    
    def is_file_processed(self, file_identifier: str) -> bool:
        """Проверяет, был ли файл уже обработан"""
        return file_identifier in self.processed_files
    
    def mark_file_processed(self, file_identifier: str) -> None:
        """Отмечает файл как обработанный"""
        self.processed_files.add(file_identifier)
    
    def is_key_tested(self, api_key: str) -> bool:
        """Проверяет, был ли ключ уже протестирован"""
        # Маскируем ключ для безопасного хранения
        masked_key = self._mask_key_for_cache(api_key)
        return masked_key in self.tested_keys
    
    def mark_key_tested(self, api_key: str) -> None:
        """Отмечает ключ как протестированный"""
        # Маскируем ключ для безопасного хранения
        masked_key = self._mask_key_for_cache(api_key)
        self.tested_keys.add(masked_key)
    
    def _mask_key_for_cache(self, api_key: str) -> str:
        """
        Маскирует ключ для безопасного хранения в кэше
        
        Args:
            api_key: Исходный API ключ
            
        Returns:
            str: Маскированный ключ
        """
        if len(api_key) <= 8:
            return "*" * len(api_key)
        
        # Сохраняем только первые 4 и последние 4 символа + хэш
        import hashlib
        key_hash = hashlib.md5(api_key.encode()).hexdigest()[:8]
        return f"{api_key[:4]}***{api_key[-4:]}_{key_hash}"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику кэша
        
        Returns:
            Dict: Статистика кэша
        """
        return {
            'processed_files': len(self.processed_files),
            'tested_keys': len(self.tested_keys),
            'cache_file_exists': os.path.exists(self.cache_file),
            'cache_file_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
    
    def auto_save_threshold(self, threshold: int = 10) -> bool:
        """
        Проверяет, нужно ли автоматически сохранить кэш
        
        Args:
            threshold: Порог количества новых записей для автосохранения
            
        Returns:
            bool: True если нужно сохранить
        """
        return len(self.processed_files) % threshold == 0