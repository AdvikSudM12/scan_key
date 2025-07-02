#!/usr/bin/env python3
"""
Улучшенный скрипт для поиска и валидации API ключей различных AI-провайдеров в GitHub репозиториях
Версия 4.0 с архитектурным разделением и поддержкой асинхронности (backward compatibility wrapper)
"""

import requests
import re
import time
import json
import os
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import quote
import base64
import openai
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ai_providers_key_patterns import AI_PROVIDERS_PATTERNS, AIProvider, get_all_patterns

# Импорты новой архитектуры
from validators import ValidatorFactory
from cache_manager import CacheManager
from github_client import GitHubClient

# Загружаем переменные окружения из .env файла
load_dotenv()


class EnhancedMultiProviderGitHubScanner:
    def __init__(self, github_token: str = None):
        """
        Инициализация мульти-провайдерного сканера (backward compatibility wrapper)
        
        Args:
            github_token: Токен GitHub API для увеличения лимитов запросов
        """
        # Используем новую архитектуру под капотом
        self.github_client = GitHubClient(github_token)
        self.cache_manager = CacheManager()
        self.validator_factory = ValidatorFactory()
        
        # Backward compatibility атрибуты
        self.github_token = github_token
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        # Структура для хранения валидных ключей по провайдерам
        self.valid_keys = {
            'openai': [],
            'anthropic': [],
            'google_gemini': []
        }
        
        # Backward compatibility для кэша
        self.tested_keys = set()
        self.processed_files = set()
        self.cache_file = 'scanner_cache.json'
        self.processed_repos_file = 'processed_repositories.json'
        
        # Файлы для сохранения результатов
        self.valid_keys_files = {
            'openai': 'valid_openai_keys.json',
            'anthropic': 'valid_anthropic_keys.json',
            'google_gemini': 'valid_google_gemini_keys.json'
        }
        
        # Загружаем кэш и валидные ключи при инициализации
        self.ensure_files_exist()
        self.load_cache()
        self.load_all_valid_keys()
        
        print(f"Инициализирован мульти-провайдерный сканер {'с токеном GitHub' if github_token else 'без токена GitHub'}")

    def load_cache(self):
        """
        Загружает кэш обработанных файлов и протестированных ключей (backward compatibility)
        """
        # Синхронизируем с новым cache_manager
        cache_stats = self.cache_manager.get_stats()
        self.processed_files = self.cache_manager.processed_files.copy()
        self.tested_keys = self.cache_manager.tested_keys.copy()
        
        print(f"📂 Загружен кэш: {cache_stats['processed_files']} файлов, {cache_stats['tested_keys']} ключей")

    def ensure_files_exist(self):
        """
        Проверяет существование необходимых файлов для всех провайдеров и создает их при необходимости
        """
        # Создаем файлы для каждого провайдера
        for provider, filename in self.valid_keys_files.items():
            if not os.path.exists(filename):
                initial_data = {
                    'scan_info': {
                        'timestamp': datetime.now().isoformat(),
                        'total_keys_tested': 0,
                        'valid_keys_found': 0,
                        'files_processed': 0,
                        'success_rate': "0%",
                        'provider': provider
                    },
                    'valid_keys': []
                }
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(initial_data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Создан файл для {provider.upper()}: {filename}")
                except Exception as e:
                    print(f"⚠️ Ошибка создания файла {provider}: {e}")
        
        # Создаем файл кэша если не существует
        if not os.path.exists(self.cache_file):
            initial_cache = {
                'processed_files': [],
                'tested_keys': [],
                'last_updated': datetime.now().isoformat()
            }
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_cache, f, indent=2, ensure_ascii=False)
                print(f"✅ Создан файл кэша: {self.cache_file}")
            except Exception as e:
                print(f"⚠️ Ошибка создания файла кэша: {e}")

    def save_cache(self):
        """
        Сохраняет кэш обработанных файлов и протестированных ключей (backward compatibility)
        """
        self.cache_manager.save_cache()

    def clear_cache(self):
        """
        Очищает кэш (backward compatibility)
        """
        self.cache_manager.clear_cache()
        self.processed_files = set()
        self.tested_keys = set()

    def get_cache_stats(self):
        """
        Возвращает статистику кэша (backward compatibility)
        """
        return self.cache_manager.get_stats()

    def test_validation_function(self, test_key: str) -> bool:
        """
        Тестирует функцию валидации с известным ключом
        
        Args:
            test_key: API ключ для тестирования
            
        Returns:
            True если функция валидации работает корректно
        """
        print("🧪 Тестирование функции валидации...")
        print(f"   Тестовый ключ: {test_key[:15]}...{test_key[-10:]} (длина: {len(test_key)})")
        
        try:
            result = self.validate_openai_key(test_key)
            if result:
                print("✅ Функция валидации работает корректно!")
                print("   Тестовый ключ успешно валидирован")
                return True
            else:
                print("❌ Функция валидации вернула False для тестового ключа")
                print("   Возможно, ключ невалидный или есть проблемы с API")
                return False
        except Exception as e:
            print(f"❌ Ошибка при тестировании функции валидации: {e}")
            return False

    def get_search_queries(self, include_recent: bool = True) -> List[str]:
        """
        Генерирует список поисковых запросов
        
        Args:
            include_recent: Включать ли фильтры по свежести
            
        Returns:
            Список поисковых запросов
        """
        base_queries = [
            # === OpenAI ===
            'OPENAI_API_KEY',
            'sk- AND openai',
            'openai.api_key',
            '"sk-" AND (openai OR gpt)',
            'sk-proj AND openai',
            '"sk-proj-" AND api',
            'OPENAI_API_KEY AND .env',
            'OPENAI_API_KEY AND config',
            'openai_api_key AND settings',
            'openai.api_key AND python',
            'OpenAI AND javascript',
            'OPENAI_API_KEY AND README',
            'openai AND setup',
            'OPENAI_API_KEY AND dockerfile',
            'openai AND docker-compose',
            
            # === Anthropic (Claude) ===
            'ANTHROPIC_API_KEY',
            'CLAUDE_API_KEY',
            'sk-ant AND anthropic',
            '"sk-ant-" AND claude',
            'anthropic AND api_key',
            'claude AND api_key',
            'ANTHROPIC_API_KEY AND .env',
            'CLAUDE_API_KEY AND config',
            'anthropic_api_key AND settings',
            'anthropic AND python',
            'claude AND javascript',
            'ANTHROPIC_API_KEY AND README',
            'anthropic AND setup',
            'ANTHROPIC_API_KEY AND dockerfile',
            'claude AND docker-compose',
            
            # === Google Gemini ===
            'GOOGLE_API_KEY',
            'GEMINI_API_KEY',
            'AIza AND google',
            '"AIza" AND gemini',
            'google AND api_key',
            'gemini AND api_key',
            'GOOGLE_API_KEY AND .env',
            'GEMINI_API_KEY AND config',
            'google_api_key AND settings',
            'gemini AND python',
            'google.generativeai AND javascript',
            'GOOGLE_API_KEY AND README',
            'gemini AND setup',
            'GOOGLE_API_KEY AND dockerfile',
            'gemini AND docker-compose',
            
            # === Универсальные запросы ===
            'api_key AND (openai OR anthropic OR google OR gemini OR claude)',
            '"API_KEY" AND (AI OR GPT OR LLM)',
            'env AND (OPENAI OR ANTHROPIC OR GOOGLE OR GEMINI)',
        ]
        
        if include_recent:
            # Добавляем фильтры для поиска свежих файлов
            recent_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            recent_queries = [
                # OpenAI
                f'sk- pushed:>{recent_date}',
                f'OPENAI_API_KEY created:>{recent_date}',
                f'openai api_key updated:>{recent_date}',
                # Anthropic
                f'sk-ant pushed:>{recent_date}',
                f'ANTHROPIC_API_KEY created:>{recent_date}',
                f'anthropic api_key updated:>{recent_date}',
                # Google
                f'AIza pushed:>{recent_date}',
                f'GOOGLE_API_KEY created:>{recent_date}',
                f'gemini api_key updated:>{recent_date}',
            ]
            base_queries.extend(recent_queries)
        
        return base_queries

    def search_github_code(self, query: str, max_pages: int = 5, sort_by: str = "indexed") -> List[Dict]:
        """
        Поиск кода в GitHub по запросу с улучшенной обработкой ошибок и проверкой лимитов
        """
        results = []
        
        for page in range(1, max_pages + 1):
            # Проверяем лимиты перед каждым запросом
            if not self.should_continue_scanning():
                print(f"🛑 Остановка поиска из-за исчерпания лимитов API")
                break
            
            try:
                url = f"https://api.github.com/search/code"
                params = {
                    'q': query,
                    'page': page,
                    'per_page': 100,
                    'sort': sort_by,
                    'order': 'desc'
                }
                
                response = self.session.get(url, params=params)
                
                if response.status_code == 403:
                    # Проверяем, не связано ли это с лимитами
                    if 'rate limit' in response.text.lower():
                        print(f"🛑 Достигнут лимит запросов для поиска")
                        self.wait_for_rate_limit_reset('search')
                        continue
                    
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    if reset_time:
                        reset_datetime = datetime.fromtimestamp(int(reset_time))
                        wait_time = (reset_datetime - datetime.now()).total_seconds()
                        print(f"⏰ Лимит запросов. Ожидание {int(wait_time/60)} минут до {reset_datetime.strftime('%H:%M:%S')}")
                        time.sleep(min(wait_time, 3600))  # Максимум час ожидания
                    else:
                        time.sleep(60)
                    continue
                    
                if response.status_code == 422:
                    print(f"❌ Слишком много результатов для запроса: {query}")
                    break
                    
                if response.status_code != 200:
                    print(f"❌ Ошибка {response.status_code} для запроса: {query}")
                    break
                    
                data = response.json()
                
                if 'items' not in data:
                    break
                
                print(f"  📄 Страница {page}: {len(data['items'])} файлов")
                results.extend(data['items'])
                
                if len(data['items']) < 100:
                    break
                    
                # Адаптивная пауза между запросами
                time.sleep(2 if self.github_token else 10)
                
            except Exception as e:
                print(f"❌ Ошибка при поиске '{query}': {e}")
                break
                
        return results

    def get_file_content(self, file_info: Dict) -> str:
        """
        Получение содержимого файла с улучшенной обработкой и проверкой лимитов
        """
        try:
            url = file_info.get('url')
            if not url:
                return ""
            
            # Проверяем размер файла
            file_size = file_info.get('size', 0)
            if file_size > 1048576:  # 1MB
                print(f"    📏 Пропускаем большой файл ({file_size} байт)")
                return ""
                
            response = self.session.get(url)
            
            if response.status_code == 403:
                # Проверяем лимиты Core API
                if 'rate limit' in response.text.lower():
                    print("    🛑 Достигнут лимит Core API при получении файла")
                    self.wait_for_rate_limit_reset('core')
                    return ""
                else:
                    print("    ⚠️ Доступ к файлу ограничен (403)")
                    time.sleep(60)
                    return ""
                
            if response.status_code != 200:
                print(f"    ❌ Ошибка {response.status_code} при получении файла")
                return ""
                
            data = response.json()
            
            if data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
                
        except Exception as e:
            print(f"    ❌ Ошибка при получении файла: {e}")
            
        return ""

    def extract_api_keys(self, content: str) -> Set[str]:
        """
        Расширенное извлечение API ключей всех поддерживаемых провайдеров из содержимого файла
        """
        keys = set()
        
        # Используем паттерны из модуля ai_providers_key_patterns
        all_patterns = get_all_patterns()
        
        # Основной поиск по базовым паттернам всех провайдеров
        for pattern in all_patterns:
            matches = pattern.findall(content)
            for match in matches:
                key = match.strip() if isinstance(match, str) else str(match).strip()
                if len(key) >= 20:  # Минимальная длина ключа
                    keys.add(key)
        
        # Расширенные контекстные паттерны для всех провайдеров
        context_patterns = [
            # OpenAI ключи в кавычках различных типов
            r'["\']sk-[A-Za-z0-9\-_]{20,200}["\']',
            r'[`]sk-[A-Za-z0-9\-_]{20,200}[`]',
            
            # Anthropic ключи
            r'["\']sk-ant-[A-Za-z0-9\-_]{20,200}["\']',
            r'[`]sk-ant-[A-Za-z0-9\-_]{20,200}[`]',
            
            # Google Gemini ключи
            r'["\']AIza[A-Za-z0-9\-_]{35}["\']',
            r'[`]AIza[A-Za-z0-9\-_]{35}[`]',
            
            # Переменные окружения - OpenAI
            r'(?i)(?:OPENAI_API_KEY|OPENAI_KEY|API_KEY)[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Переменные окружения - Anthropic
            r'(?i)(?:ANTHROPIC_API_KEY|CLAUDE_API_KEY|ANTHROPIC_KEY)[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?(sk-ant-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Переменные окружения - Google
            r'(?i)(?:GOOGLE_API_KEY|GEMINI_API_KEY|GOOGLE_AI_KEY)[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?(AIza[A-Za-z0-9\-_]{35})["\']?',
            
            # Настройки в коде - общие
            r'(?i)(?:openai|anthropic|claude|google|gemini)[_\.](?:api[_\.])?key[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            r'(?i)(?:api_key|apikey|token)[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            
            # JSON/YAML форматы
            r'["\'](?:api_key|openai_api_key|anthropic_api_key|google_api_key|key|token)["\'][^a-zA-Z0-9]*:[^a-zA-Z0-9]*["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Python специфичные
            r'(?i)api_key\s*=\s*[rf]?["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            r'(?i)(?:OpenAI|Anthropic|Claude)\s*\([^)]*api_key\s*=\s*[rf]?["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            
            # JavaScript/TypeScript
            r'(?i)(?:api_?key|apikey)\s*:\s*["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            
            # HTTP заголовки
            r'(?i)Authorization[^a-zA-Z0-9]*:[^a-zA-Z0-9]*Bearer\s+((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})',
            r'(?i)X-API-Key[^a-zA-Z0-9]*:[^a-zA-Z0-9]*["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            r'(?i)x-api-key[^a-zA-Z0-9]*:[^a-zA-Z0-9]*["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Командная строка
            r'(?i)--(?:api-)?key\s+["\']?((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})["\']?',
            
            # URL параметры
            r'(?i)(?:api_key|key)=((?:sk-|AIza)[A-Za-z0-9\-_]{20,200})',
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    key = next((m for m in reversed(match) if m), "")
                else:
                    key = match
                    
                key = key.strip('\'"` \t\n\r;,')
                
                if len(key) >= 20 and (key.startswith(('sk-', 'AIza'))):
                    keys.add(key)
        
        # Финальный поиск "голых" ключей всех типов
        loose_patterns = [
            r'\bsk-[A-Za-z0-9\-_]{20,200}\b',  # OpenAI и Anthropic
            r'\bAIza[A-Za-z0-9\-_]{35}\b',     # Google Gemini
        ]
        
        for loose_pattern in loose_patterns:
            loose_matches = re.findall(loose_pattern, content)
            for key in loose_matches:
                if len(key) >= 20:
                    keys.add(key)
        
        return keys

    def validate_openai_key(self, api_key: str) -> bool:
        """
        Улучшенная валидация API ключа OpenAI (backward compatibility)
        """
        validator = self.validator_factory.create_validator('openai')
        if validator:
            return validator.validate_sync(api_key)
        return False

    def validate_anthropic_key(self, api_key: str) -> bool:
        """
        Валидация API ключа Anthropic (Claude) (backward compatibility)
        """
        validator = self.validator_factory.create_validator('anthropic')
        if validator:
            return validator.validate_sync(api_key)
        return False

    def validate_google_gemini_key(self, api_key: str) -> bool:
        """
        Валидация API ключа Google Gemini (backward compatibility)
        """
        validator = self.validator_factory.create_validator('google_gemini')
        if validator:
            return validator.validate_sync(api_key)
        return False

    def validate_api_key(self, api_key: str, provider: str) -> bool:
        """
        Универсальный метод валидации API ключа в зависимости от провайдера (backward compatibility)
        
        Args:
            api_key: API-ключ для валидации
            provider: Провайдер ключа
            
        Returns:
            bool: True если ключ валидный
        """
        validator = self.validator_factory.create_validator(provider)
        if validator:
            return validator.validate_sync(api_key)
        else:
            print(f"⚠️ Неизвестный провайдер для валидации: {provider}")
            return False

    def scan_repositories(self, max_pages_per_query: int = 3, sort_by: str = "updated") -> List[Dict]:
        """
        Основной метод сканирования с улучшенной логикой
        """
        print("🔍 Запуск улучшенного сканирования GitHub репозиториев")
        print(f"📊 Сортировка: {sort_by}")
        print(f"📄 Страниц на запрос: {max_pages_per_query}")
        
        # Проверяем лимиты API перед началом сканирования
        self.print_rate_limits()
        
        if not self.should_continue_scanning():
            print("❌ Сканирование отменено из-за недостатка лимитов API")
            return []
        
        # Показываем статистику кэша
        cache_stats = self.get_cache_stats()
        print(f"📂 Кэш: {cache_stats['processed_files']} файлов, {cache_stats['tested_keys']} ключей")
        
        search_queries = self.get_search_queries(include_recent=True)
        files_processed_in_session = 0
        
        try:
            for i, query in enumerate(search_queries, 1):
                print(f"\n🔎 Запрос {i}/{len(search_queries)}: {query}")
                
                files = self.search_github_code(query, max_pages_per_query, sort_by)
                print(f"📁 Найдено файлов: {len(files)}")
                
                # Фильтруем уже обработанные файлы
                new_files = [f for f in files if f.get('url') not in self.processed_files]
                if len(new_files) < len(files):
                    print(f"   🔄 Пропущено уже обработанных: {len(files) - len(new_files)}")
                
                for j, file_info in enumerate(new_files, 1):
                    file_url = file_info.get('url')
                    self.processed_files.add(file_url)
                    files_processed_in_session += 1
                    
                    repo_info = file_info.get('repository', {})
                    file_name = file_info.get('name', 'unknown')
                    updated_at = repo_info.get('updated_at', 'unknown')[:10]
                    
                    print(f"📄 Файл {j}/{len(new_files)}: {file_name} (обновлен: {updated_at})")
                    
                    content = self.get_file_content(file_info)
                    if not content:
                        continue
                    
                    api_keys = self.extract_api_keys(content)
                    
                    for key in api_keys:
                        if key in self.tested_keys:
                            key_preview = f"{key[:15]}...{key[-10:]}" if len(key) > 25 else key[:20] + "..."
                            print(f"🔄 Ключ уже тестировался: {key_preview}")
                            continue
                            
                        self.tested_keys.add(key)
                        key_preview = f"{key[:15]}...{key[-10:]}" if len(key) > 25 else key[:20] + "..."
                        
                        # Идентифицируем провайдера
                        provider = self.identify_provider(key)
                        if not provider:
                            print(f"⚠️ Неопознанный формат ключа: {key_preview}")
                            continue
                        
                        print(f"🔑 Тестируем {provider.upper()} ключ: {key_preview} (длина: {len(key)})")
                        
                        if self.validate_api_key(key, provider):
                            print(f"✅ ВАЛИДНЫЙ {provider.upper()} КЛЮЧ НАЙДЕН!")
                            key_data = {
                                'api_key': key,
                                'provider': provider,
                                'repository': repo_info.get('full_name', 'unknown'),
                                'file_path': file_info.get('path', 'unknown'),
                                'file_url': file_info.get('html_url', ''),
                                'updated_at': updated_at,
                                'size': file_info.get('size', 0),
                                'found_at': datetime.now().isoformat(),
                                'validation_status': 'valid'
                            }
                            
                            # Добавляем в локальный кэш
                            self.valid_keys[provider].append(key_data)
                            
                            # Сохраняем валидный ключ сразу в соответствующий файл
                            key_info_for_file = {k: v for k, v in key_data.items() if k != 'api_key'}
                            self.add_valid_key_to_file(key, provider, key_info_for_file)
                        else:
                            print(f"❌ {provider.upper()} ключ невалидный")
                        
                        # Увеличенная пауза для избежания блокировки
                        time.sleep(4)
                    
                    # Сохраняем кэш каждые 10 обработанных файлов
                    if files_processed_in_session % 10 == 0:
                        print(f"💾 Сохранение промежуточного прогресса...")
                        self.save_cache()
                        
                        # Проверяем лимиты каждые 10 файлов
                        if files_processed_in_session % 20 == 0:
                            print(f"🔍 Проверка лимитов API...")
                            if not self.should_continue_scanning():
                                print(f"🛑 Остановка сканирования из-за исчерпания лимитов")
                                return self.valid_keys
                        
        except KeyboardInterrupt:
            print(f"\n⏹️ Сканирование прервано пользователем")
            print(f"💾 Сохранение прогресса...")
            self.save_cache()
            raise
        
        # Сохраняем финальный кэш
        self.save_cache()
        print(f"\n📊 В этой сессии обработано новых файлов: {files_processed_in_session}")
        
        return self.valid_keys

    def save_results(self, filename: str = None):
        if filename is None:
            filename = os.getenv('OUTPUT_FILE', 'enhanced_valid_openai_keys.json')
        """
        Обновление статистики в файле результатов (НЕ перезаписывает ключи)
        """
        try:
            # Читаем существующие данные
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'valid_keys': []}
            
            # Обновляем только статистику
            data['scan_info'] = {
                'timestamp': datetime.now().isoformat(),
                'total_keys_tested': len(self.tested_keys),
                'valid_keys_found': len(data.get('valid_keys', [])),
                'files_processed': len(self.processed_files),
                'success_rate': f"{len(data.get('valid_keys', []))/len(self.tested_keys)*100:.2f}%" if self.tested_keys else "0%"
            }
            
            # Сохраняем обновленные данные
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 СТАТИСТИКА СКАНИРОВАНИЯ")
            print(f"{'='*50}")
            print(f"🔍 Всего протестировано ключей: {len(self.tested_keys)}")
            print(f"✅ Валидных ключей найдено: {len(data.get('valid_keys', []))}")
            print(f"📁 Обработано файлов: {len(self.processed_files)}")
            print(f"📈 Процент успеха: {data['scan_info']['success_rate']}")
            print(f"💾 Статистика обновлена в: {filename}")
            
        except Exception as e:
            print(f"⚠️ Ошибка обновления статистики: {e}")
    
    def add_valid_key_to_file(self, api_key: str, provider: str, key_info: dict):
        """
        Добавляет валидный ключ в соответствующий файл провайдера
        
        Args:
            api_key: Валидный API-ключ
            provider: Провайдер ключа
            key_info: Дополнительная информация о ключе
        """
        filename = self.valid_keys_files.get(provider)
        if not filename:
            print(f"⚠️ Неизвестный провайдер: {provider}")
            return
            
        try:
            # Загружаем существующие данные
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    'scan_info': {
                        'timestamp': datetime.now().isoformat(),
                        'total_keys_tested': 0,
                        'valid_keys_found': 0,
                        'files_processed': 0,
                        'success_rate': "0%",
                        'provider': provider
                    },
                    'valid_keys': []
                }
            
            # Проверяем, что ключ еще не добавлен
            existing_keys = [key['api_key'] for key in data['valid_keys']]
            if api_key not in existing_keys:
                # Добавляем новый ключ
                new_key_entry = {
                    'api_key': api_key,
                    'provider': provider,
                    'found_timestamp': datetime.now().isoformat(),
                    'validation_status': 'valid',
                    **key_info
                }
                data['valid_keys'].append(new_key_entry)
                
                # Обновляем статистику
                data['scan_info']['valid_keys_found'] = len(data['valid_keys'])
                data['scan_info']['last_updated'] = datetime.now().isoformat()
                
                # Сохраняем файл
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Обновляем локальный кэш
                self.valid_keys[provider].append(new_key_entry)
                
                print(f"✅ {provider.upper()}: Добавлен валидный ключ в {filename}")
            else:
                print(f"ℹ️ {provider.upper()}: Ключ уже существует в файле")
                
        except Exception as e:
            print(f"⚠️ Ошибка сохранения валидного ключа {provider}: {e}")

    def identify_provider(self, api_key: str) -> Optional[str]:
        """
        Идентифицирует провайдера по формату API-ключа (backward compatibility)
        
        Args:
            api_key: API-ключ для идентификации
            
        Returns:
            str: Название провайдера или None если не удалось идентифицировать
        """
        return self.validator_factory.identify_provider(api_key)

    def load_all_valid_keys(self):
        """
        Загружает все существующие валидные ключи из файлов для каждого провайдера
        """
        for provider, filename in self.valid_keys_files.items():
            try:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        existing_keys = data.get('valid_keys', [])
                        self.valid_keys[provider] = existing_keys
                        
                    print(f"📄 {provider.upper()}: Загружено {len(existing_keys)} существующих валидных ключей")
                else:
                    # Создаем файл если не существует
                    initial_data = {
                        'scan_info': {
                            'timestamp': datetime.now().isoformat(),
                            'total_keys_tested': 0,
                            'valid_keys_found': 0,
                            'files_processed': 0,
                            'success_rate': "0%",
                            'provider': provider
                        },
                        'valid_keys': []
                    }
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(initial_data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Создан файл для {provider.upper()}: {filename}")
                    
            except Exception as e:
                print(f"⚠️ Ошибка загрузки валидных ключей {provider}: {e}")
                self.valid_keys[provider] = []

    def check_rate_limits(self) -> Dict:
        """
        Проверяет текущие лимиты GitHub API
        
        Returns:
            Словарь с информацией о лимитах
        """
        try:
            response = self.session.get("https://api.github.com/rate_limit")
            
            if response.status_code == 200:
                data = response.json()
                
                # Извлекаем информацию о лимитах для поиска кода
                search_limits = data.get('resources', {}).get('search', {})
                core_limits = data.get('resources', {}).get('core', {})
                
                return {
                    'search': {
                        'limit': search_limits.get('limit', 0),
                        'remaining': search_limits.get('remaining', 0),
                        'reset_time': search_limits.get('reset', 0),
                        'reset_datetime': datetime.fromtimestamp(search_limits.get('reset', 0)) if search_limits.get('reset') else None
                    },
                    'core': {
                        'limit': core_limits.get('limit', 0),
                        'remaining': core_limits.get('remaining', 0),
                        'reset_time': core_limits.get('reset', 0),
                        'reset_datetime': datetime.fromtimestamp(core_limits.get('reset', 0)) if core_limits.get('reset') else None
                    },
                    'status': 'success'
                }
            else:
                return {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def print_rate_limits(self):
        """
        Выводит информацию о текущих лимитах GitHub API
        """
        print("🔍 Проверка лимитов GitHub API...")
        limits = self.check_rate_limits()
        
        if limits['status'] == 'success':
            search = limits['search']
            core = limits['core']
            
            print(f"📊 ЛИМИТЫ GITHUB API")
            print("-" * 50)
            print(f"🔎 Search API:")
            print(f"   Лимит: {search['limit']} запросов/час")
            print(f"   Осталось: {search['remaining']} запросов")
            if search['reset_datetime']:
                print(f"   Сброс: {search['reset_datetime'].strftime('%H:%M:%S')}")
            
            print(f"🌐 Core API:")
            print(f"   Лимит: {core['limit']} запросов/час")
            print(f"   Осталось: {core['remaining']} запросов")
            if core['reset_datetime']:
                print(f"   Сброс: {core['reset_datetime'].strftime('%H:%M:%S')}")
            
            # Предупреждения о низких лимитах
            if search['remaining'] < 10:
                print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: Осталось мало запросов для Search API!")
            
            if core['remaining'] < 100:
                print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: Осталось мало запросов для Core API!")
                
        else:
            print(f"❌ Ошибка получения лимитов: {limits.get('error', 'Неизвестная ошибка')}")
        
        print("-" * 50)

    def should_continue_scanning(self) -> bool:
        """
        Проверяет, можно ли продолжать сканирование на основе лимитов API
        
        Returns:
            True если можно продолжать, False если лимиты исчерпаны
        """
        limits = self.check_rate_limits()
        
        if limits['status'] != 'success':
            print(f"⚠️ Не удалось проверить лимиты: {limits.get('error')}")
            return True  # Продолжаем, если не удалось проверить
        
        search_remaining = limits['search']['remaining']
        core_remaining = limits['core']['remaining']
        
        # Минимальные требования для продолжения
        min_search_requests = 5   # Для поиска файлов
        min_core_requests = 20    # Для получения содержимого файлов
        
        if search_remaining < min_search_requests:
            reset_time = limits['search']['reset_datetime']
            if reset_time:
                wait_minutes = (reset_time - datetime.now()).total_seconds() / 60
                print(f"🛑 Исчерпаны запросы Search API ({search_remaining} осталось). Ожидание {wait_minutes:.1f} минут до сброса.")
            else:
                print(f"🛑 Исчерпаны запросы Search API ({search_remaining} осталось).")
            return False
        
        if core_remaining < min_core_requests:
            reset_time = limits['core']['reset_datetime']
            if reset_time:
                wait_minutes = (reset_time - datetime.now()).total_seconds() / 60
                print(f"🛑 Исчерпаны запросы Core API ({core_remaining} осталось). Ожидание {wait_minutes:.1f} минут до сброса.")
            else:
                print(f"🛑 Исчерпаны запросы Core API ({core_remaining} осталось).")
            return False
        
        # Предупреждения о низких лимитах
        if search_remaining < min_search_requests * 2:
            print(f"⚠️ Мало запросов Search API: {search_remaining}")
        
        if core_remaining < min_core_requests * 2:
            print(f"⚠️ Мало запросов Core API: {core_remaining}")
        
        return True

    def wait_for_rate_limit_reset(self, api_type: str = 'search'):
        """
        Ожидает сброса лимитов для указанного типа API
        
        Args:
            api_type: 'search' или 'core'
        """
        limits = self.check_rate_limits()
        
        if limits['status'] != 'success':
            print(f"⚠️ Не удалось получить информацию о лимитах, ожидание 60 секунд...")
            time.sleep(60)
            return
        
        api_limits = limits.get(api_type, {})
        reset_datetime = api_limits.get('reset_datetime')
        
        if reset_datetime:
            wait_time = (reset_datetime - datetime.now()).total_seconds()
            if wait_time > 0:
                wait_minutes = wait_time / 60
                print(f"⏰ Ожидание сброса лимитов {api_type.upper()} API: {wait_minutes:.1f} минут...")
                
                # Ждем с периодическими обновлениями
                while wait_time > 0:
                    if wait_time > 300:  # Больше 5 минут
                        print(f"   Осталось ждать: {wait_time/60:.1f} минут")
                        time.sleep(60)  # Проверяем каждую минуту
                        wait_time -= 60
                    else:
                        time.sleep(wait_time)
                        break
                
                print(f"✅ Лимиты {api_type.upper()} API должны быть сброшены")
            else:
                print(f"✅ Лимиты {api_type.upper()} API уже сброшены")
        else:
            print(f"⚠️ Не удалось определить время сброса лимитов, ожидание 60 секунд...")
            time.sleep(60)
    

def main():
    """
    Основная функция запуска мульти-провайдерного сканера
    """
    print("🚀 ENHANCED MULTI-PROVIDER GITHUB SCANNER v3.0")
    print("🤖 Поддержка: OpenAI, Anthropic (Claude), Google Gemini")
    print("👨‍💻 Автор: PRIZRAKJJ | Telegram: t.me/SafeVibeCode")
    print("="*70)
    
    github_token = os.getenv('GITHUB_TOKEN')
    scanner = EnhancedMultiProviderGitHubScanner(github_token)
    
    # Проверяем аргументы командной строки для очистки кэша
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['--clear-cache', '--reset', '-r']:
        print("\n🗑️ ОЧИСТКА КЭША")
        print("-" * 50)
        scanner.clear_cache()
        print("Кэш очищен. Перезапустите сканер для начала с чистого листа.")
        return
    
    # Показываем справку по кэшу
    cache_stats = scanner.get_cache_stats()
    if cache_stats['processed_files'] > 0:
        print(f"\n📂 ИНФОРМАЦИЯ О КЭШЕ")
        print("-" * 50)
        print(f"🗂️ Обработанных файлов: {cache_stats['processed_files']}")
        print(f"🔑 Протестированных ключей: {cache_stats['tested_keys']}")
        print(f"💾 Размер кэша: {cache_stats['cache_file_size']} байт")
        print("\n💡 Для очистки кэша запустите: python enhanced_scanner.py --clear-cache")
        print("="*60)
    
    # Тестирование функций валидации для всех провайдеров
    print("\n🔧 ТЕСТИРОВАНИЕ ФУНКЦИЙ ВАЛИДАЦИИ")
    print("-" * 60)
    
    # Проверяем наличие тестовых ключей в .env
    test_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'anthropic': os.getenv('ANTHROPIC_API_KEY'), 
        'google_gemini': os.getenv('GOOGLE_API_KEY')
    }
    
    available_keys = {k: v for k, v in test_keys.items() if v}
    
    if available_keys:
        print("🧪 Найдены тестовые ключи в .env файле:")
        validation_results = {}
        
        for provider, key in available_keys.items():
            print(f"\n🤖 Тестирование {provider.upper()}:")
            key_preview = f"{key[:15]}...{key[-10:]}" if len(key) > 25 else key[:20] + "..."
            print(f"   Тестовый ключ: {key_preview} (длина: {len(key)})")
            
            try:
                is_valid = scanner.validate_api_key(key, provider)
                validation_results[provider] = is_valid
                
                if is_valid:
                    print(f"   ✅ Функция валидации {provider.upper()} работает корректно!")
                else:
                    print(f"   ❌ Тестовый ключ {provider.upper()} невалидный или есть проблемы с API")
                    
            except Exception as e:
                print(f"   ⚠️ Ошибка тестирования {provider.upper()}: {e}")
                validation_results[provider] = False
        
        # Итоговый результат
        working_validators = sum(1 for result in validation_results.values() if result)
        total_validators = len(validation_results)
        
        print(f"\n📊 РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ:")
        print(f"   ✅ Работающих валидаторов: {working_validators}/{total_validators}")
        
        if working_validators == 0:
            print("\n⚠️  ПРЕДУПРЕЖДЕНИЕ: Ни одна функция валидации не работает!")
            print("   Рекомендуется проверить:")
            print("   - Валидность API ключей в .env файле")
            print("   - Подключение к интернету")
            print("   - Квоты и лимиты API провайдеров")
            
            response = input("\nПродолжить сканирование? (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'д', 'да']:
                print("Сканирование отменено пользователем.")
                return
        elif working_validators < total_validators:
            print(f"\n⚠️  Частичная работоспособность: {working_validators}/{total_validators} валидаторов работают")
            print("   Сканирование будет продолжено, но некоторые ключи могут быть пропущены")
        
        print("\n" + "="*70)
    else:
        print("⚠️  Тестовые API ключи не найдены в .env файле")
        print("   Функции валидации не будут протестированы заранее")
        print("   Валидация будет проверена на найденных ключах")
        print("   Для полного тестирования добавьте ключи в .env:")
        print("   - OPENAI_API_KEY=sk-...")
        print("   - ANTHROPIC_API_KEY=sk-ant-...")
        print("   - GOOGLE_API_KEY=AIza...")
        print("\n" + "="*70)
    
    try:
        print("\n🔍 ЗАПУСК МУЛЬТИ-ПРОВАЙДЕРНОГО СКАНИРОВАНИЯ")
        print("-" * 50)
        valid_keys = scanner.scan_repositories(max_pages_per_query=2, sort_by="updated")
        
        # Выводим статистику по каждому провайдеру
        print(f"\n🎉 НАЙДЕННЫЕ ВАЛИДНЫЕ КЛЮЧИ ПО ПРОВАЙДЕРАМ:")
        print("="*60)
        
        total_found = 0
        for provider in ['openai', 'anthropic', 'google_gemini']:
            provider_keys = valid_keys.get(provider, [])
            total_found += len(provider_keys)
            
            print(f"\n🤖 {provider.upper().replace('_', ' ')}:")
            if provider_keys:
                for i, key_info in enumerate(provider_keys, 1):
                    key_preview = f"{key_info['api_key'][:15]}...{key_info['api_key'][-10:]}"
                    print(f"   {i}. 🔑 {key_preview}")
                    print(f"      📦 Репозиторий: {key_info['repository']}")
                    print(f"      📄 Файл: {key_info['file_path']}")
                    print(f"      🕒 Обновлен: {key_info['updated_at']}")
            else:
                print(f"   ❌ Валидные ключи не найдены")
        
        print(f"\n📊 ИТОГО: {total_found} валидных ключей найдено")
        
        if total_found == 0:
            print("\n🤷 Валидные ключи не найдены в этом сканировании")
        
    except KeyboardInterrupt:
        print("\n⏹️ Сканирование прервано пользователем")
        print("💾 Сохранение кэша...")
        scanner.save_cache()
    except Exception as e:
        print(f"\n❌ Ошибка во время сканирования: {e}")
        print("💾 Сохранение кэша...")
        scanner.save_cache()


if __name__ == "__main__":
    main()
