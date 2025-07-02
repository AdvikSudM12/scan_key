"""
Модуль управления конфигурацией для сканера API ключей
"""

import yaml
import os
import argparse
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class ScanConfig:
    """Конфигурация для сканирования"""
    max_pages_per_query: int = 3
    delay_between_requests: float = 1.0
    delay_between_key_tests: float = 2.0
    max_concurrent_files: int = 10
    timeout_seconds: int = 30
    include_recent: bool = True
    recent_days: int = 30


@dataclass
class CacheConfig:
    """Конфигурация кэша"""
    cache_file: str = 'scanner_cache.json'
    auto_save_threshold: int = 10
    use_sqlite: bool = False
    sqlite_file: str = 'scanner_cache.db'


@dataclass
class LoggingConfig:
    """Конфигурация логгирования"""
    level: str = 'INFO'
    file: str = 'scanner.log'
    max_size_mb: int = 10
    backup_count: int = 5
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


@dataclass
class SecurityConfig:
    """Конфигурация безопасности"""
    mask_keys_in_logs: bool = True
    mask_keys_in_cache: bool = True
    mask_keys_in_output: bool = True
    save_full_keys: bool = False


@dataclass
class GitHubConfig:
    """Конфигурация GitHub API"""
    token: Optional[str] = None
    api_url: str = 'https://api.github.com'
    user_agent: str = 'Enhanced-Multi-Provider-Scanner/4.0'
    rate_limit_buffer: int = 5


@dataclass
class Config:
    """Основная конфигурация приложения"""
    scan: ScanConfig
    cache: CacheConfig
    logging: LoggingConfig
    security: SecurityConfig
    github: GitHubConfig
    
    # Файлы для сохранения результатов
    output_files: Dict[str, str]
    
    def __init__(self):
        self.scan = ScanConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        self.github = GitHubConfig()
        
        self.output_files = {
            'openai': 'valid_openai_keys.json',
            'anthropic': 'valid_anthropic_keys.json',
            'google_gemini': 'valid_google_gemini_keys.json'
        }


class ConfigManager:
    """Менеджер конфигурации"""
    
    DEFAULT_CONFIG_FILE = 'config.yaml'
    ENV_PREFIX = 'SCANNER_'
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Инициализация менеджера конфигурации
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = Config()
    
    def load_config(self) -> Config:
        """
        Загружает конфигурацию из различных источников в порядке приоритета:
        1. Аргументы командной строки
        2. Переменные окружения
        3. Файл конфигурации YAML
        4. Значения по умолчанию
        
        Returns:
            Config: Загруженная конфигурация
        """
        # 1. Загружаем из файла YAML
        self._load_from_yaml()
        
        # 2. Переопределяем переменными окружения
        self._load_from_env()
        
        # 3. Переопределяем аргументами командной строки
        self._load_from_args()
        
        return self.config
    
    def _load_from_yaml(self):
        """Загружает конфигурацию из YAML файла"""
        if not os.path.exists(self.config_file):
            print(f"📄 Файл конфигурации {self.config_file} не найден, используем значения по умолчанию")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data:
                self._update_config_from_dict(yaml_data)
                print(f"📄 Конфигурация загружена из {self.config_file}")
                
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации из {self.config_file}: {e}")
    
    def _load_from_env(self):
        """Загружает конфигурацию из переменных окружения"""
        env_mappings = {
            f'{self.ENV_PREFIX}GITHUB_TOKEN': ('github', 'token'),
            f'{self.ENV_PREFIX}MAX_PAGES': ('scan', 'max_pages_per_query'),
            f'{self.ENV_PREFIX}DELAY_REQUESTS': ('scan', 'delay_between_requests'),
            f'{self.ENV_PREFIX}DELAY_TESTS': ('scan', 'delay_between_key_tests'),
            f'{self.ENV_PREFIX}MAX_CONCURRENT': ('scan', 'max_concurrent_files'),
            f'{self.ENV_PREFIX}CACHE_FILE': ('cache', 'cache_file'),
            f'{self.ENV_PREFIX}USE_SQLITE': ('cache', 'use_sqlite'),
            f'{self.ENV_PREFIX}LOG_LEVEL': ('logging', 'level'),
            f'{self.ENV_PREFIX}LOG_FILE': ('logging', 'file'),
            f'{self.ENV_PREFIX}MASK_KEYS': ('security', 'mask_keys_in_logs'),
        }
        
        # Также поддерживаем стандартные переменные
        if os.getenv('GITHUB_TOKEN'):
            self.config.github.token = os.getenv('GITHUB_TOKEN')
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_config_value(section, key, value)
    
    def _load_from_args(self):
        """Загружает конфигурацию из аргументов командной строки"""
        parser = argparse.ArgumentParser(description='Enhanced Multi-Provider GitHub Scanner')
        
        # Основные параметры
        parser.add_argument('--config', type=str, help='Путь к файлу конфигурации')
        parser.add_argument('--github-token', type=str, help='Токен GitHub API')
        parser.add_argument('--max-pages', type=int, help='Максимальное количество страниц на запрос')
        parser.add_argument('--delay-requests', type=float, help='Задержка между запросами (сек)')
        parser.add_argument('--delay-tests', type=float, help='Задержка между тестами ключей (сек)')
        parser.add_argument('--max-concurrent', type=int, help='Максимальное количество одновременных файлов')
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Уровень логгирования')
        parser.add_argument('--log-file', type=str, help='Файл для логов')
        parser.add_argument('--cache-file', type=str, help='Файл кэша')
        parser.add_argument('--use-sqlite', action='store_true', help='Использовать SQLite для кэша')
        parser.add_argument('--no-mask-keys', action='store_true', help='Не маскировать ключи в выводе')
        
        # Управление
        parser.add_argument('--clear-cache', action='store_true', help='Очистить кэш перед запуском')
        parser.add_argument('--async-mode', action='store_true', help='Использовать асинхронный режим')
        parser.add_argument('--test-mode', action='store_true', help='Режим тестирования (только валидация)')
        
        # Парсим только известные аргументы, чтобы не конфликтовать с другими частями приложения
        args, unknown = parser.parse_known_args()
        
        # Применяем аргументы к конфигурации
        if args.github_token:
            self.config.github.token = args.github_token
        if args.max_pages:
            self.config.scan.max_pages_per_query = args.max_pages
        if args.delay_requests:
            self.config.scan.delay_between_requests = args.delay_requests
        if args.delay_tests:
            self.config.scan.delay_between_key_tests = args.delay_tests
        if args.max_concurrent:
            self.config.scan.max_concurrent_files = args.max_concurrent
        if args.log_level:
            self.config.logging.level = args.log_level
        if args.log_file:
            self.config.logging.file = args.log_file
        if args.cache_file:
            self.config.cache.cache_file = args.cache_file
        if args.use_sqlite:
            self.config.cache.use_sqlite = True
        if args.no_mask_keys:
            self.config.security.mask_keys_in_logs = False
            self.config.security.mask_keys_in_output = False
    
    def _update_config_from_dict(self, data: Dict[str, Any]):
        """Обновляет конфигурацию из словаря"""
        for section_name, section_data in data.items():
            if hasattr(self.config, section_name) and isinstance(section_data, dict):
                section = getattr(self.config, section_name)
                for key, value in section_data.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
            elif section_name == 'output_files' and isinstance(section_data, dict):
                self.config.output_files.update(section_data)
    
    def _set_config_value(self, section: str, key: str, value: str):
        """Устанавливает значение конфигурации с автоматическим преобразованием типов"""
        if hasattr(self.config, section):
            section_obj = getattr(self.config, section)
            if hasattr(section_obj, key):
                current_value = getattr(section_obj, key)
                
                # Преобразуем тип значения
                if isinstance(current_value, bool):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, float):
                    value = float(value)
                
                setattr(section_obj, key, value)
    
    def save_config(self, file_path: Optional[str] = None):
        """
        Сохраняет текущую конфигурацию в YAML файл
        
        Args:
            file_path: Путь для сохранения (по умолчанию используется текущий файл конфигурации)
        """
        save_path = file_path or self.config_file
        
        config_dict = {
            'scan': {
                'max_pages_per_query': self.config.scan.max_pages_per_query,
                'delay_between_requests': self.config.scan.delay_between_requests,
                'delay_between_key_tests': self.config.scan.delay_between_key_tests,
                'max_concurrent_files': self.config.scan.max_concurrent_files,
                'timeout_seconds': self.config.scan.timeout_seconds,
                'include_recent': self.config.scan.include_recent,
                'recent_days': self.config.scan.recent_days
            },
            'cache': {
                'cache_file': self.config.cache.cache_file,
                'auto_save_threshold': self.config.cache.auto_save_threshold,
                'use_sqlite': self.config.cache.use_sqlite,
                'sqlite_file': self.config.cache.sqlite_file
            },
            'logging': {
                'level': self.config.logging.level,
                'file': self.config.logging.file,
                'max_size_mb': self.config.logging.max_size_mb,
                'backup_count': self.config.logging.backup_count,
                'format': self.config.logging.format
            },
            'security': {
                'mask_keys_in_logs': self.config.security.mask_keys_in_logs,
                'mask_keys_in_cache': self.config.security.mask_keys_in_cache,
                'mask_keys_in_output': self.config.security.mask_keys_in_output,
                'save_full_keys': self.config.security.save_full_keys
            },
            'github': {
                'api_url': self.config.github.api_url,
                'user_agent': self.config.github.user_agent,
                'rate_limit_buffer': self.config.github.rate_limit_buffer
            },
            'output_files': self.config.output_files
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, indent=2)
            print(f"✅ Конфигурация сохранена в {save_path}")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения конфигурации: {e}")
    
    def create_default_config(self, file_path: Optional[str] = None):
        """
        Создает файл конфигурации по умолчанию
        
        Args:
            file_path: Путь для создания файла
        """
        save_path = file_path or self.config_file
        if not os.path.exists(save_path):
            self.save_config(save_path)
            print(f"📄 Создан файл конфигурации по умолчанию: {save_path}")
        else:
            print(f"📄 Файл конфигурации уже существует: {save_path}")
    
    def print_config(self):
        """Выводит текущую конфигурацию"""
        print("\n📋 ТЕКУЩАЯ КОНФИГУРАЦИЯ")
        print("=" * 50)
        
        print(f"\n🔍 Сканирование:")
        print(f"   Максимум страниц на запрос: {self.config.scan.max_pages_per_query}")
        print(f"   Задержка между запросами: {self.config.scan.delay_between_requests}с")
        print(f"   Задержка между тестами: {self.config.scan.delay_between_key_tests}с")
        print(f"   Максимум одновременных файлов: {self.config.scan.max_concurrent_files}")
        print(f"   Таймаут: {self.config.scan.timeout_seconds}с")
        print(f"   Включать недавние: {self.config.scan.include_recent}")
        
        print(f"\n💾 Кэш:")
        print(f"   Файл кэша: {self.config.cache.cache_file}")
        print(f"   Автосохранение каждые: {self.config.cache.auto_save_threshold} файлов")
        print(f"   Использовать SQLite: {self.config.cache.use_sqlite}")
        
        print(f"\n📝 Логгирование:")
        print(f"   Уровень: {self.config.logging.level}")
        print(f"   Файл: {self.config.logging.file}")
        print(f"   Максимальный размер: {self.config.logging.max_size_mb}MB")
        
        print(f"\n🔒 Безопасность:")
        print(f"   Маскировать ключи в логах: {self.config.security.mask_keys_in_logs}")
        print(f"   Маскировать ключи в кэше: {self.config.security.mask_keys_in_cache}")
        print(f"   Маскировать ключи в выводе: {self.config.security.mask_keys_in_output}")
        
        print(f"\n🐙 GitHub:")
        print(f"   Токен настроен: {'✅' if self.config.github.token else '❌'}")
        print(f"   API URL: {self.config.github.api_url}")
        print(f"   User-Agent: {self.config.github.user_agent}")
        
        print(f"\n📄 Файлы результатов:")
        for provider, file_path in self.config.output_files.items():
            print(f"   {provider}: {file_path}")
        
        print("=" * 50)