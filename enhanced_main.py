#!/usr/bin/env python3
"""
Enhanced Multi-Provider GitHub Scanner v4.0 - Основной CLI интерфейс
С архитектурным разделением, асинхронностью, улучшенным логгированием и аналитикой
"""

import asyncio
import sys
import os
import time
from typing import Optional

# Локальные импорты
from config_manager import ConfigManager
from enhanced_logging import ScannerLogger, ProgressTracker
from analytics import AnalyticsManager
from enhanced_async_scanner import EnhancedAsyncGitHubScanner
from enhanced_scanner import EnhancedMultiProviderGitHubScanner  # Backward compatibility
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class EnhancedScannerCLI:
    """Основной CLI интерфейс для улучшенного сканера"""
    
    def __init__(self):
        """Инициализация CLI"""
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Инициализация логгера
        self.logger = ScannerLogger(self.config.logging)
        
        # Инициализация аналитики
        self.analytics = AnalyticsManager()
        
        # Прогресс трекер
        self.progress_tracker = ProgressTracker(self.logger)
        
        # Сканеры
        self.async_scanner: Optional[EnhancedAsyncGitHubScanner] = None
        self.sync_scanner: Optional[EnhancedMultiProviderGitHubScanner] = None
    
    def print_banner(self):
        """Выводит баннер приложения"""
        self.logger.print_header(
            "🚀 ENHANCED MULTI-PROVIDER GITHUB SCANNER v4.0",
            "Поиск и валидация API ключей с архитектурным разделением и асинхронностью\n"
            "Поддержка: OpenAI, Anthropic (Claude), Google Gemini\n"
            "👨‍💻 Автор: PRIZRAKJJ | Telegram: t.me/SafeVibeCode"
        )
    
    def check_environment(self):
        """Проверяет окружение и конфигурацию"""
        self.logger.print_section("ПРОВЕРКА ОКРУЖЕНИЯ")
        
        # Проверяем токен GitHub
        if self.config.github.token:
            self.logger.success("GitHub токен настроен")
        else:
            self.logger.warning("GitHub токен не настроен - будут действовать ограниченные лимиты API")
        
        # Проверяем тестовые ключи для валидации
        test_keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'Google Gemini': os.getenv('GOOGLE_API_KEY')
        }
        
        available_keys = {k: v for k, v in test_keys.items() if v}
        
        if available_keys:
            self.logger.success(f"Найдены тестовые ключи для {len(available_keys)} провайдеров")
            for provider in available_keys.keys():
                self.logger.info(f"   ✅ {provider}")
        else:
            self.logger.warning("Тестовые API ключи не найдены в переменных окружения")
            self.logger.info("   Для полного тестирования добавьте ключи в .env:")
            self.logger.info("   - OPENAI_API_KEY=sk-...")
            self.logger.info("   - ANTHROPIC_API_KEY=sk-ant-...")
            self.logger.info("   - GOOGLE_API_KEY=AIza...")
        
        # Показываем текущую конфигурацию
        self.config_manager.print_config()
    
    def handle_special_commands(self) -> bool:
        """
        Обрабатывает специальные команды
        
        Returns:
            bool: True если команда обработана и нужно завершить выполнение
        """
        import argparse
        
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--clear-cache', action='store_true')
        parser.add_argument('--show-analytics', action='store_true')
        parser.add_argument('--export-report', type=str)
        parser.add_argument('--create-config', action='store_true')
        parser.add_argument('--test-validation', action='store_true')
        parser.add_argument('--async-mode', action='store_true')
        parser.add_argument('--help', action='store_true')
        
        args, unknown = parser.parse_known_args()
        
        if args.help:
            self.show_help()
            return True
        
        if args.create_config:
            self.config_manager.create_default_config()
            return True
        
        if args.clear_cache:
            self.clear_cache()
            return True
        
        if args.show_analytics:
            self.show_analytics()
            return True
        
        if args.export_report:
            self.export_analytics_report(args.export_report)
            return True
        
        if args.test_validation:
            self.test_validation_functions()
            return True
        
        return False
    
    def show_help(self):
        """Показывает справку"""
        self.logger.print_section("СПРАВКА ПО ИСПОЛЬЗОВАНИЮ")
        
        help_text = """
🔧 Параметры командной строки:
   --async-mode             Использовать асинхронный режим (рекомендуется)
   --config PATH           Путь к файлу конфигурации
   --github-token TOKEN    Токен GitHub API
   --max-pages N           Максимальное количество страниц на запрос
   --delay-requests N      Задержка между запросами (сек)
   --log-level LEVEL       Уровень логгирования (DEBUG, INFO, WARNING, ERROR)
   --clear-cache           Очистить кэш перед запуском
   --test-validation       Тестировать функции валидации
   --show-analytics        Показать аналитику
   --export-report FILE    Экспортировать отчет аналитики
   --create-config         Создать файл конфигурации по умолчанию
   --help                  Показать эту справку

📄 Файлы конфигурации:
   config.yaml             Основная конфигурация
   .env                    Переменные окружения (токены, ключи)

🔍 Режимы работы:
   Асинхронный режим       Быстрая параллельная обработка файлов
   Синхронный режим        Совместимость с существующими скриптами

📊 Аналитика:
   scanner_analytics.json  История сканирований и статистика
   scanner.log            Подробные логи работы

🔐 Безопасность:
   Все ключи автоматически маскируются в логах и выводе
   Полные ключи сохраняются только в защищенных файлах результатов
        """
        
        print(help_text)
    
    def clear_cache(self):
        """Очищает кэш"""
        self.logger.print_section("ОЧИСТКА КЭША")
        
        # Инициализируем сканер для доступа к кэшу
        scanner = EnhancedMultiProviderGitHubScanner(self.config.github.token)
        scanner.clear_cache()
        
        self.logger.success("Кэш очищен")
    
    def show_analytics(self):
        """Показывает аналитику"""
        self.logger.print_section("АНАЛИТИКА СКАНИРОВАНИЯ")
        
        # Текущая статистика
        if self.analytics.current_session:
            current_stats = self.analytics.get_current_stats()
            self.logger.print_stats_table(current_stats, "Текущая сессия")
        
        # Историческая статистика
        historical_stats = self.analytics.get_historical_stats(30)
        if historical_stats:
            self.logger.print_stats_table(historical_stats, "Последние 30 дней")
        
        # Анализ трендов
        trends = self.analytics.get_trends_analysis()
        if trends:
            self.logger.print_stats_table(trends, "Анализ трендов")
    
    def export_analytics_report(self, file_path: str):
        """Экспортирует отчет аналитики"""
        self.logger.print_section("ЭКСПОРТ ОТЧЕТА")
        self.analytics.export_report(file_path)
    
    def test_validation_functions(self):
        """Тестирует функции валидации"""
        self.logger.print_section("ТЕСТИРОВАНИЕ ФУНКЦИЙ ВАЛИДАЦИИ")
        
        # Инициализируем сканер
        scanner = EnhancedMultiProviderGitHubScanner(self.config.github.token)
        
        # Проверяем наличие тестовых ключей
        test_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'google_gemini': os.getenv('GOOGLE_API_KEY')
        }
        
        available_keys = {k: v for k, v in test_keys.items() if v}
        
        if not available_keys:
            self.logger.warning("Тестовые ключи не найдены в переменных окружения")
            return
        
        validation_results = {}
        
        for provider, key in available_keys.items():
            self.logger.info(f"\n🧪 Тестирование {provider.upper()}")
            masked_key = f"{key[:8]}***{key[-4:]}"
            self.logger.info(f"   Ключ: {masked_key}")
            
            try:
                is_valid = scanner.validate_api_key(key, provider)
                validation_results[provider] = is_valid
                
                if is_valid:
                    self.logger.success(f"Валидация {provider.upper()} работает корректно")
                else:
                    self.logger.failure(f"Ключ {provider.upper()} невалидный или есть проблемы")
            except Exception as e:
                self.logger.error(f"Ошибка валидации {provider.upper()}: {e}")
                validation_results[provider] = False
        
        # Итоговый результат
        working_validators = sum(1 for result in validation_results.values() if result)
        total_validators = len(validation_results)
        
        self.logger.print_stats_table({
            'Протестированных валидаторов': total_validators,
            'Работающих валидаторов': working_validators,
            'Успешность': f"{working_validators/total_validators*100:.1f}%" if total_validators > 0 else "0%"
        }, "Результаты тестирования")
    
    async def run_async_scan(self) -> dict:
        """Запускает асинхронное сканирование"""
        self.logger.print_section("АСИНХРОННОЕ СКАНИРОВАНИЕ")
        
        # Инициализируем асинхронный сканер
        self.async_scanner = EnhancedAsyncGitHubScanner(self.config.github.token)
        
        # Запускаем сессию аналитики
        session_id = self.analytics.start_session(config=self.config.__dict__)
        self.logger.info(f"Начата сессия аналитики: {session_id}")
        
        start_time = time.time()
        
        try:
            # Запускаем сканирование
            results = await self.async_scanner.scan_repositories_async(
                max_pages_per_query=self.config.scan.max_pages_per_query
            )
            
            scan_time = time.time() - start_time
            
            # Записываем результаты в аналитику
            self.analytics.end_session()
            
            # Логируем итоги
            total_valid = sum(len(keys) for keys in results.values())
            current_stats = self.analytics.get_current_stats()
            
            self.logger.log_scan_summary(
                current_stats.get('files_processed', 0),
                current_stats.get('keys_found', 0),
                total_valid,
                scan_time
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка во время асинхронного сканирования: {e}")
            self.analytics.record_error('scan_error', str(e))
            return {}
    
    def run_sync_scan(self) -> dict:
        """Запускает синхронное сканирование"""
        self.logger.print_section("СИНХРОННОЕ СКАНИРОВАНИЕ")
        
        # Инициализируем синхронный сканер
        self.sync_scanner = EnhancedMultiProviderGitHubScanner(self.config.github.token)
        
        # Запускаем сессию аналитики
        session_id = self.analytics.start_session(config=self.config.__dict__)
        self.logger.info(f"Начата сессия аналитики: {session_id}")
        
        start_time = time.time()
        
        try:
            # Запускаем сканирование
            results = self.sync_scanner.scan_repositories(
                max_pages_per_query=self.config.scan.max_pages_per_query
            )
            
            scan_time = time.time() - start_time
            
            # Записываем результаты в аналитику
            self.analytics.end_session()
            
            # Логируем итоги
            total_valid = sum(len(keys) for keys in results.values())
            current_stats = self.analytics.get_current_stats()
            
            self.logger.log_scan_summary(
                current_stats.get('files_processed', 0),
                current_stats.get('keys_found', 0),
                total_valid,
                scan_time
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка во время синхронного сканирования: {e}")
            self.analytics.record_error('scan_error', str(e))
            return {}
    
    def print_results(self, results: dict):
        """Выводит результаты сканирования"""
        self.logger.print_section("РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ")
        
        total_found = sum(len(keys) for keys in results.values())
        
        if total_found == 0:
            self.logger.info("🤷 Валидные ключи не найдены в этом сканировании")
            return
        
        for provider in ['openai', 'anthropic', 'google_gemini']:
            provider_keys = results.get(provider, [])
            
            self.logger.info(f"\n🤖 {provider.upper().replace('_', ' ')}:")
            
            if provider_keys:
                for i, key_info in enumerate(provider_keys, 1):
                    # Маскируем ключ если включена безопасность
                    if self.config.security.mask_keys_in_output:
                        key_display = key_info.get('masked_key', 'ключ маскирован')
                    else:
                        key_display = f"{key_info['api_key'][:8]}***{key_info['api_key'][-4:]}"
                    
                    self.logger.info(f"   {i}. 🔑 {key_display}")
                    self.logger.info(f"      📦 Репозиторий: {key_info['repository']}")
                    self.logger.info(f"      📄 Файл: {key_info['file_path']}")
                    if key_info.get('found_at'):
                        self.logger.info(f"      🕒 Найден: {key_info['found_at']}")
            else:
                self.logger.info("   ❌ Валидные ключи не найдены")
        
        self.logger.success(f"ИТОГО: {total_found} валидных ключей найдено")
    
    async def main(self):
        """Основная функция CLI"""
        try:
            # Показываем баннер
            self.print_banner()
            
            # Обрабатываем специальные команды
            if self.handle_special_commands():
                return
            
            # Проверяем окружение
            self.check_environment()
            
            # Определяем режим работы
            import argparse
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument('--async-mode', action='store_true')
            args, unknown = parser.parse_known_args()
            
            use_async = args.async_mode
            
            if use_async:
                self.logger.info("🚀 Используется асинхронный режим")
                results = await self.run_async_scan()
            else:
                self.logger.info("🔄 Используется синхронный режим (backward compatibility)")
                results = self.run_sync_scan()
            
            # Выводим результаты
            self.print_results(results)
            
        except KeyboardInterrupt:
            self.logger.warning("\n⏹️ Сканирование прервано пользователем")
            if self.analytics.current_session:
                self.analytics.end_session()
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка: {e}")
            if self.analytics.current_session:
                self.analytics.record_error('critical_error', str(e))
                self.analytics.end_session()
        finally:
            # Показываем финальную аналитику
            if hasattr(self, 'analytics'):
                final_stats = self.analytics.get_current_stats()
                if final_stats:
                    self.logger.print_stats_table(final_stats, "Финальная статистика")


def main():
    """Точка входа в приложение"""
    cli = EnhancedScannerCLI()
    
    # Проверяем, поддерживается ли asyncio
    try:
        asyncio.run(cli.main())
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()