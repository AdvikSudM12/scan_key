"""
Улучшенный скрипт для поиска и валидации API ключей различных AI-провайдеров в GitHub репозиториях
Версия 4.0 с архитектурным разделением, асинхронностью и улучшенной безопасностью
"""

import asyncio
import logging
import re
import json
import os
from typing import List, Dict, Set, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Импорты для прогресс-бара и логгирования
from tqdm.asyncio import tqdm
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.logging import RichHandler

# Локальные импорты
from validators import ValidatorFactory
from cache_manager import CacheManager
from github_client import GitHubClient
from ai_providers_key_patterns import get_all_patterns
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler("scanner.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)
console = Console()


class EnhancedAsyncGitHubScanner:
    """
    Улучшенный асинхронный сканер GitHub репозиториев для поиска API ключей
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Инициализация сканера
        
        Args:
            github_token: Токен GitHub API
        """
        self.github_client = GitHubClient(github_token)
        self.cache_manager = CacheManager()
        self.validator_factory = ValidatorFactory()
        
        # Структура для хранения найденных валидных ключей
        self.valid_keys = {
            'openai': [],
            'anthropic': [],
            'google_gemini': []
        }
        
        # Файлы для сохранения результатов
        self.valid_keys_files = {
            'openai': 'valid_openai_keys.json',
            'anthropic': 'valid_anthropic_keys.json',
            'google_gemini': 'valid_google_gemini_keys.json'
        }
        
        self.console = Console()
        
        # Инициализация файлов результатов
        self._ensure_files_exist()
        self._load_all_valid_keys()
        
        logger.info(f"Инициализирован асинхронный сканер {'с токеном GitHub' if github_token else 'без токена GitHub'}")
    
    def _ensure_files_exist(self):
        """Создает файлы для сохранения валидных ключей если они не существуют"""
        for provider, filename in self.valid_keys_files.items():
            if not os.path.exists(filename):
                initial_data = {
                    'provider': provider,
                    'valid_keys': [],
                    'last_updated': datetime.now().isoformat(),
                    'total_found': 0
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
                
                console.print(f"✅ Создан файл для {provider.upper()}: {filename}")
    
    def _load_all_valid_keys(self):
        """Загружает все существующие валидные ключи из файлов"""
        for provider, filename in self.valid_keys_files.items():
            try:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.valid_keys[provider] = data.get('valid_keys', [])
                        
                console.print(f"📄 {provider.upper()}: Загружено {len(self.valid_keys[provider])} существующих валидных ключей")
                
            except Exception as e:
                logger.error(f"Ошибка загрузки валидных ключей {provider}: {e}")
                self.valid_keys[provider] = []
    
    def extract_api_keys(self, content: str) -> List[str]:
        """
        Извлекает потенциальные API ключи из содержимого файла
        
        Args:
            content: Содержимое файла
            
        Returns:
            List[str]: Список найденных ключей
        """
        keys = []
        patterns = get_all_patterns()
        
        for pattern in patterns:
            matches = pattern.findall(content)
            keys.extend(matches)
        
        # Удаляем дубликаты и фильтруем слишком короткие ключи
        unique_keys = list(set(keys))
        filtered_keys = [key for key in unique_keys if len(key) >= 20]
        
        return filtered_keys
    
    async def validate_key_async(self, api_key: str, provider: str) -> bool:
        """
        Асинхронная валидация API ключа
        
        Args:
            api_key: API ключ для валидации
            provider: Провайдер ключа
            
        Returns:
            bool: True если ключ валидный
        """
        # Проверяем кэш
        if self.cache_manager.is_key_tested(api_key):
            logger.debug(f"Ключ {self._mask_key(api_key)} уже протестирован (кэш)")
            return False
        
        validator = self.validator_factory.create_validator(provider)
        if not validator:
            logger.warning(f"Неизвестный провайдер для валидации: {provider}")
            return False
        
        try:
            is_valid = await validator.validate_async(api_key)
            
            # Отмечаем ключ как протестированный
            self.cache_manager.mark_key_tested(api_key)
            
            if is_valid:
                logger.info(f"✅ Найден валидный ключ {provider.upper()}: {self._mask_key(api_key)}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Ошибка валидации ключа {provider}: {e}")
            return False
    
    def validate_key_sync(self, api_key: str, provider: str) -> bool:
        """
        Синхронная валидация API ключа (для backward compatibility)
        
        Args:
            api_key: API ключ для валидации
            provider: Провайдер ключа
            
        Returns:
            bool: True если ключ валидный
        """
        # Проверяем кэш
        if self.cache_manager.is_key_tested(api_key):
            logger.debug(f"Ключ {self._mask_key(api_key)} уже протестирован (кэш)")
            return False
        
        validator = self.validator_factory.create_validator(provider)
        if not validator:
            logger.warning(f"Неизвестный провайдер для валидации: {provider}")
            return False
        
        try:
            is_valid = validator.validate_sync(api_key)
            
            # Отмечаем ключ как протестированный
            self.cache_manager.mark_key_tested(api_key)
            
            if is_valid:
                logger.info(f"✅ Найден валидный ключ {provider.upper()}: {self._mask_key(api_key)}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Ошибка валидации ключа {provider}: {e}")
            return False
    
    def _mask_key(self, api_key: str) -> str:
        """Маскирует API ключ для безопасного логгирования"""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
    
    async def process_file_async(self, file_info: Dict) -> List[Dict]:
        """
        Асинхронная обработка файла
        
        Args:
            file_info: Информация о файле из GitHub API
            
        Returns:
            List[Dict]: Список найденных валидных ключей
        """
        found_keys = []
        
        try:
            # Создаем уникальный идентификатор файла
            file_id = f"{file_info['repository']['full_name']}:{file_info['path']}:{file_info.get('sha', 'unknown')}"
            
            # Проверяем кэш
            if self.cache_manager.is_file_processed(file_id):
                logger.debug(f"Файл уже обработан (кэш): {file_info['path']}")
                return found_keys
            
            # Получаем содержимое файла
            content = await self.github_client.get_file_content_async(
                file_info['repository']['owner']['login'],
                file_info['repository']['name'],
                file_info['path']
            )
            
            if not content:
                return found_keys
            
            # Извлекаем ключи
            potential_keys = self.extract_api_keys(content)
            
            if potential_keys:
                logger.info(f"🔍 Найдено {len(potential_keys)} потенциальных ключей в {file_info['path']}")
                
                # Проверяем каждый ключ
                for api_key in potential_keys:
                    provider = self.validator_factory.identify_provider(api_key)
                    
                    if provider:
                        is_valid = await self.validate_key_async(api_key, provider)
                        
                        if is_valid:
                            key_info = {
                                'api_key': api_key,
                                'provider': provider,
                                'repository': file_info['repository']['full_name'],
                                'file_path': file_info['path'],
                                'file_url': file_info['html_url'],
                                'updated_at': file_info['repository'].get('updated_at', ''),
                                'found_at': datetime.now().isoformat()
                            }
                            
                            found_keys.append(key_info)
                            self.valid_keys[provider].append(key_info)
                            
                            # Сохраняем ключ в файл
                            await self._save_valid_key_async(api_key, provider, key_info)
                        
                        # Небольшая задержка между проверками
                        await asyncio.sleep(1)
            
            # Отмечаем файл как обработанный
            self.cache_manager.mark_file_processed(file_id)
            
            # Автосохранение кэша
            if self.cache_manager.auto_save_threshold():
                self.cache_manager.save_cache()
            
        except Exception as e:
            logger.error(f"Ошибка обработки файла {file_info.get('path', 'unknown')}: {e}")
        
        return found_keys
    
    async def _save_valid_key_async(self, api_key: str, provider: str, key_info: Dict):
        """
        Асинхронно сохраняет валидный ключ в файл
        
        Args:
            api_key: API ключ
            provider: Провайдер
            key_info: Информация о ключе
        """
        try:
            filename = self.valid_keys_files[provider]
            
            # Читаем существующие данные
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    'provider': provider,
                    'valid_keys': [],
                    'last_updated': datetime.now().isoformat(),
                    'total_found': 0
                }
            
            # Проверяем, нет ли уже такого ключа
            existing_keys = [k['api_key'] for k in data['valid_keys']]
            if api_key not in existing_keys:
                # Маскируем ключ для сохранения
                masked_key_info = key_info.copy()
                masked_key_info['api_key'] = self._mask_key(api_key)
                
                data['valid_keys'].append(masked_key_info)
                data['total_found'] = len(data['valid_keys'])
                data['last_updated'] = datetime.now().isoformat()
                
                # Сохраняем данные
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ {provider.upper()}: Добавлен валидный ключ в {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения валидного ключа {provider}: {e}")
    
    async def scan_repositories_async(self, max_pages_per_query: int = 3) -> Dict[str, List[Dict]]:
        """
        Основной асинхронный метод сканирования
        
        Args:
            max_pages_per_query: Максимальное количество страниц на запрос
            
        Returns:
            Dict[str, List[Dict]]: Словарь валидных ключей по провайдерам
        """
        console.print("🚀 Запуск асинхронного сканирования GitHub")
        
        # Получаем поисковые запросы
        queries = self.github_client.get_search_queries()
        
        all_found_keys = []
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            query_task = progress.add_task("Обработка запросов", total=len(queries))
            
            for query in queries:
                try:
                    console.print(f"🔍 Поиск: {query}")
                    
                    for page in range(1, max_pages_per_query + 1):
                        try:
                            results = await self.github_client.search_code_async(query, page)
                            items = results.get('items', [])
                            
                            if not items:
                                break
                            
                            console.print(f"   📄 Страница {page}: {len(items)} файлов")
                            
                            # Обрабатываем файлы параллельно
                            tasks = []
                            for item in items:
                                task = self.process_file_async(item)
                                tasks.append(task)
                            
                            # Ждем завершения всех задач для этой страницы
                            page_results = await asyncio.gather(*tasks, return_exceptions=True)
                            
                            for result in page_results:
                                if isinstance(result, list):
                                    all_found_keys.extend(result)
                            
                            # Небольшая задержка между страницами
                            await asyncio.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"Ошибка обработки страницы {page} для запроса '{query}': {e}")
                            break
                    
                    progress.advance(query_task)
                    
                    # Задержка между запросами
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки запроса '{query}': {e}")
                    progress.advance(query_task)
        
        # Сохраняем кэш
        self.cache_manager.save_cache()
        
        # Группируем результаты по провайдерам
        results_by_provider = {'openai': [], 'anthropic': [], 'google_gemini': []}
        for key_info in all_found_keys:
            provider = key_info.get('provider')
            if provider in results_by_provider:
                results_by_provider[provider].append(key_info)
        
        return results_by_provider
    
    def scan_repositories_sync(self, max_pages_per_query: int = 3) -> Dict[str, List[Dict]]:
        """
        Синхронный метод сканирования (для backward compatibility)
        
        Args:
            max_pages_per_query: Максимальное количество страниц на запрос
            
        Returns:
            Dict[str, List[Dict]]: Словарь валидных ключей по провайдерам
        """
        # Запускаем асинхронную версию в новом event loop
        return asyncio.run(self.scan_repositories_async(max_pages_per_query))
    
    def get_cache_stats(self) -> Dict:
        """Возвращает статистику кэша"""
        return self.cache_manager.get_stats()
    
    def clear_cache(self):
        """Очищает кэш"""
        self.cache_manager.clear_cache()