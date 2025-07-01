#!/usr/bin/env python3
"""
Улучшенный скрипт для поиска и валидации API ключей OpenAI в GitHub репозиториях
Версия 2.0 с расширенными паттернами поиска и сортировкой по свежести
"""

import requests
import re
import time
import json
import os
from typing import List, Dict, Set
from urllib.parse import quote
import base64
import openai
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загружаем переменные окружения из .env файла
load_dotenv()


class EnhancedGitHubOpenAIScanner:
    def __init__(self, github_token: str = None):
        """
        Инициализация улучшенного сканера
        
        Args:
            github_token: Токен GitHub API для увеличения лимитов запросов
        """
        self.github_token = github_token
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        self.valid_keys = []
        self.tested_keys = set()
        self.processed_files = set()
        
        # Файлы для кэширования
        self.cache_file = 'scanner_cache.json'
        self.processed_repos_file = 'processed_repositories.json'
        
        # Загружаем кэш при инициализации
        self.load_cache()
        
        # Множественные паттерны для поиска различных форматов OpenAI API ключей
        self.api_key_patterns = [
            re.compile(r'sk-[A-Za-z0-9]{48}'),  # Старый формат: 48 символов
            re.compile(r'sk-proj-[A-Za-z0-9\-_]{95,200}'),  # Новый project формат
            re.compile(r'sk-[A-Za-z0-9\-_]{40,200}'),  # Общий паттерн для любых sk- ключей
            re.compile(r'sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}'),  # Специфичный паттерн OpenAI
        ]
        
        print(f"Инициализирован сканер {'с токеном GitHub' if github_token else 'без токена GitHub'}")

    def load_cache(self):
        """
        Загружает кэш обработанных файлов и протестированных ключей
        """
        try:
            # Загружаем обработанные файлы
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

    def save_cache(self):
        """
        Сохраняет кэш обработанных файлов и протестированных ключей
        """
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

    def clear_cache(self):
        """
        Очищает кэш (удаляет файлы кэша)
        """
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            if os.path.exists(self.processed_repos_file):
                os.remove(self.processed_repos_file)
            
            self.processed_files = set()
            self.tested_keys = set()
            print("🗑️ Кэш очищен")
            
        except Exception as e:
            print(f"⚠️ Ошибка очистки кэша: {e}")

    def get_cache_stats(self):
        """
        Возвращает статистику кэша
        """
        return {
            'processed_files': len(self.processed_files),
            'tested_keys': len(self.tested_keys),
            'cache_file_exists': os.path.exists(self.cache_file),
            'cache_file_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }

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
            # Основные запросы
            'OPENAI_API_KEY',
            'sk- AND openai',
            'openai.api_key',
            '"sk-" AND (openai OR gpt)',
            
            # Новые форматы ключей
            'sk-proj AND openai',
            '"sk-proj-" AND api',
            
            # Поиск в конфигурационных файлах
            'OPENAI_API_KEY AND .env',
            'OPENAI_API_KEY AND config',
            'openai_api_key AND settings',
            
            # Поиск в коде
            'openai.api_key AND python',
            'OpenAI AND javascript',
            'api_key AND typescript',
            
            # Поиск в документации
            'OPENAI_API_KEY AND README',
            'openai AND setup',
            
            # Поиск в контейнерах
            'OPENAI_API_KEY AND dockerfile',
            'openai AND docker-compose',
        ]
        
        if include_recent:
            # Добавляем фильтры для поиска свежих файлов
            recent_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            recent_queries = [
                f'sk- pushed:>{recent_date}',
                f'OPENAI_API_KEY created:>{recent_date}',
                f'openai api_key updated:>{recent_date}',
            ]
            base_queries.extend(recent_queries)
        
        return base_queries

    def search_github_code(self, query: str, max_pages: int = 5, sort_by: str = "indexed") -> List[Dict]:
        """
        Поиск кода в GitHub по запросу с улучшенной обработкой ошибок
        """
        results = []
        
        for page in range(1, max_pages + 1):
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
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    if reset_time:
                        reset_datetime = datetime.fromtimestamp(int(reset_time))
                        wait_time = (reset_datetime - datetime.now()).total_seconds()
                        print(f"Лимит запросов. Ожидание {int(wait_time/60)} минут до {reset_datetime.strftime('%H:%M:%S')}")
                        time.sleep(min(wait_time, 3600))  # Максимум час ожидания
                    else:
                        time.sleep(60)
                    continue
                    
                if response.status_code == 422:
                    print(f"Слишком много результатов для запроса: {query}")
                    break
                    
                if response.status_code != 200:
                    print(f"Ошибка {response.status_code} для запроса: {query}")
                    break
                    
                data = response.json()
                
                if 'items' not in data:
                    break
                
                print(f"  Страница {page}: {len(data['items'])} файлов")
                results.extend(data['items'])
                
                if len(data['items']) < 100:
                    break
                    
                # Адаптивная пауза между запросами
                time.sleep(2 if self.github_token else 10)
                
            except Exception as e:
                print(f"Ошибка при поиске '{query}': {e}")
                break
                
        return results

    def get_file_content(self, file_info: Dict) -> str:
        """
        Получение содержимого файла с улучшенной обработкой
        """
        try:
            url = file_info.get('url')
            if not url:
                return ""
            
            # Проверяем размер файла
            file_size = file_info.get('size', 0)
            if file_size > 1048576:  # 1MB
                print(f"    Пропускаем большой файл ({file_size} байт)")
                return ""
                
            response = self.session.get(url)
            
            if response.status_code == 403:
                print("    Достигнут лимит API при получении файла")
                time.sleep(60)
                return ""
                
            if response.status_code != 200:
                return ""
                
            data = response.json()
            
            if data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
                
        except Exception as e:
            print(f"    Ошибка при получении файла: {e}")
            
        return ""

    def extract_api_keys(self, content: str) -> Set[str]:
        """
        Расширенное извлечение API ключей из содержимого файла
        """
        keys = set()
        
        # Применяем все базовые паттерны
        for pattern in self.api_key_patterns:
            matches = pattern.findall(content)
            keys.update(matches)
        
        # Расширенные контекстные паттерны
        context_patterns = [
            # В кавычках различных типов
            r'["\']sk-[A-Za-z0-9\-_]{20,200}["\']',
            r'[`]sk-[A-Za-z0-9\-_]{20,200}[`]',
            
            # Переменные окружения
            r'(?i)(?:OPENAI_API_KEY|OPENAI_KEY|API_KEY)[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Настройки в коде
            r'(?i)(?:openai|client)[_\.](?:api[_\.])?key[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            r'(?i)(?:api_key|apikey|token)[^a-zA-Z0-9]*[=:][^a-zA-Z0-9]*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # JSON/YAML форматы
            r'["\'](?:api_key|openai_api_key|key|token)["\'][^a-zA-Z0-9]*:[^a-zA-Z0-9]*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Python специфичные
            r'(?i)api_key\s*=\s*[rf]?["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            r'(?i)OpenAI\s*\([^)]*api_key\s*=\s*[rf]?["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # JavaScript/TypeScript
            r'(?i)(?:api_?key|apikey)\s*:\s*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # HTTP заголовки
            r'(?i)Authorization[^a-zA-Z0-9]*:[^a-zA-Z0-9]*Bearer\s+(sk-[A-Za-z0-9\-_]{20,200})',
            r'(?i)X-API-Key[^a-zA-Z0-9]*:[^a-zA-Z0-9]*["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # Командная строка
            r'(?i)--(?:api-)?key\s+["\']?(sk-[A-Za-z0-9\-_]{20,200})["\']?',
            
            # URL параметры
            r'(?i)(?:api_key|key)=(sk-[A-Za-z0-9\-_]{20,200})',
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    key = next((m for m in reversed(match) if m), "")
                else:
                    key = match
                    
                key = key.strip('\'"` \t\n\r;,')
                
                if key.startswith('sk-') and len(key) >= 20:
                    keys.add(key)
        
        # Финальный поиск "голых" ключей
        loose_pattern = r'\bsk-[A-Za-z0-9\-_]{20,200}\b'
        loose_matches = re.findall(loose_pattern, content)
        for key in loose_matches:
            if len(key) >= 20:
                keys.add(key)
        
        return keys

    def validate_openai_key(self, api_key: str) -> bool:
        """
        Улучшенная валидация API ключа OpenAI
        """
        try:
            client = OpenAI(api_key=api_key)
            response = client.models.list()
            
            if response and hasattr(response, 'data'):
                return len(response.data) > 0
                
        except Exception as e:
            error_str = str(e).lower()
            if any(err in error_str for err in ['invalid api key', 'invalid_api_key', 'unauthorized', 'incorrect api key']):
                return False
            elif any(err in error_str for err in ['quota', 'rate limit', 'billing']):
                print(f"    Ключ валидный, но есть ограничения: {error_str}")
                return True
            else:
                print(f"    Неизвестная ошибка: {error_str}")
                
        return False

    def scan_repositories(self, max_pages_per_query: int = 3, sort_by: str = "updated") -> List[Dict]:
        """
        Основной метод сканирования с улучшенной логикой
        """
        print("🔍 Запуск улучшенного сканирования GitHub репозиториев")
        print(f"📊 Сортировка: {sort_by}")
        print(f"📄 Страниц на запрос: {max_pages_per_query}")
        
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
                        print(f"🔑 Тестируем ключ: {key_preview} (длина: {len(key)})")
                        
                        if self.validate_openai_key(key):
                            print(f"✅ ВАЛИДНЫЙ КЛЮЧ НАЙДЕН!")
                            self.valid_keys.append({
                                'key': key,
                                'repository': repo_info.get('full_name', 'unknown'),
                                'file_path': file_info.get('path', 'unknown'),
                                'file_url': file_info.get('html_url', ''),
                                'updated_at': updated_at,
                                'size': file_info.get('size', 0),
                                'found_at': datetime.now().isoformat()
                            })
                        else:
                            print(f"❌ Ключ невалидный")
                        
                        # Увеличенная пауза для избежания блокировки
                        time.sleep(4)
                    
                    # Сохраняем кэш каждые 10 обработанных файлов
                    if files_processed_in_session % 10 == 0:
                        print(f"💾 Сохранение промежуточного прогресса...")
                        self.save_cache()
                        
        except KeyboardInterrupt:
            print(f"\n⏹️ Сканирование прервано пользователем")
            print(f"💾 Сохранение прогресса...")
            self.save_cache()
            raise
        
        # Сохраняем финальный кэш
        self.save_cache()
        print(f"\n📊 В этой сессии обработано новых файлов: {files_processed_in_session}")
        
        return self.valid_keys

    def save_results(self, filename: str = 'enhanced_valid_openai_keys.json'):
        """
        Сохранение результатов с дополнительной информацией
        """
        results = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'total_keys_tested': len(self.tested_keys),
                'valid_keys_found': len(self.valid_keys),
                'files_processed': len(self.processed_files),
                'success_rate': f"{len(self.valid_keys)/len(self.tested_keys)*100:.2f}%" if self.tested_keys else "0%"
            },
            'valid_keys': self.valid_keys
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 СТАТИСТИКА СКАНИРОВАНИЯ")
        print(f"{'='*50}")
        print(f"🔍 Всего протестировано ключей: {len(self.tested_keys)}")
        print(f"✅ Валидных ключей найдено: {len(self.valid_keys)}")
        print(f"📁 Обработано файлов: {len(self.processed_files)}")
        print(f"📈 Процент успеха: {results['scan_info']['success_rate']}")
        print(f"💾 Результаты сохранены в: {filename}")


def main():
    """
    Основная функция запуска улучшенного сканера
    """
    print("🚀 ENHANCED GITHUB OPENAI SCANNER v2.1 (с кэшированием)")
    print("="*60)
    
    github_token = os.getenv('GITHUB_TOKEN')
    scanner = EnhancedGitHubOpenAIScanner(github_token)
    
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
    
    # Проверяем наличие OPENAI_API_KEY в .env для тестирования функции валидации
    test_openai_key = os.getenv('OPENAI_API_KEY')
    if test_openai_key:
        print("\n🔧 ТЕСТИРОВАНИЕ ФУНКЦИИ ВАЛИДАЦИИ")
        print("-" * 50)
        validation_works = scanner.test_validation_function(test_openai_key)
        
        if not validation_works:
            print("\n⚠️  ПРЕДУПРЕЖДЕНИЕ: Функция валидации может работать некорректно!")
            print("   Рекомендуется проверить:")
            print("   - Валидность OPENAI_API_KEY в .env файле")
            print("   - Подключение к интернету")
            print("   - Квоты и лимиты OpenAI API")
            
            response = input("\nПродолжить сканирование? (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'д', 'да']:
                print("Сканирование отменено пользователем.")
                return
        
        print("\n" + "="*60)
    else:
        print("\n⚠️  OPENAI_API_KEY не найден в .env файле")
        print("   Функция валидации не будет протестирована заранее")
        print("   Валидация будет проверена на найденных ключах")
        print("\n" + "="*60)
    
    try:
        print("\n🔍 ЗАПУСК ОСНОВНОГО СКАНИРОВАНИЯ")
        print("-" * 50)
        valid_keys = scanner.scan_repositories(max_pages_per_query=2, sort_by="updated")
        scanner.save_results()
        
        if valid_keys:
            print(f"\n🎉 НАЙДЕННЫЕ ВАЛИДНЫЕ КЛЮЧИ:")
            for i, key_info in enumerate(valid_keys, 1):
                key_preview = f"{key_info['key'][:15]}...{key_info['key'][-10:]}"
                print(f"{i}. 🔑 {key_preview}")
                print(f"   📦 Репозиторий: {key_info['repository']}")
                print(f"   📄 Файл: {key_info['file_path']}")
                print(f"   🕒 Обновлен: {key_info['updated_at']}")
                print()
        else:
            print("\n🤷 Валидные ключи не найдены в этом сканировании")
        
    except KeyboardInterrupt:
        print("\n⏹️ Сканирование прервано пользователем")
        print("💾 Сохранение кэша...")
        scanner.save_cache()
        scanner.save_results('partial_enhanced_results.json')
    except Exception as e:
        print(f"\n❌ Ошибка во время сканирования: {e}")
        print("💾 Сохранение кэша...")
        scanner.save_cache()
        scanner.save_results('error_enhanced_results.json')


if __name__ == "__main__":
    main()
