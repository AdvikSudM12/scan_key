"""
Улучшенная система логгирования для сканера API ключей
"""

import logging
import logging.handlers
import sys
import os
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from config_manager import LoggingConfig


class MaskedFormatter(logging.Formatter):
    """Форматтер логов с маскировкой API ключей"""
    
    KEY_PATTERNS = [
        (r'sk-[a-zA-Z0-9]{48,}', lambda m: f'sk-***{m.group()[-4:]}'),
        (r'sk-ant-[a-zA-Z0-9]{40,}', lambda m: f'sk-ant-***{m.group()[-4:]}'),
        (r'AIza[a-zA-Z0-9]{35,}', lambda m: f'AIza***{m.group()[-4:]}')
    ]
    
    def format(self, record):
        """Форматирует запись лога с маскировкой ключей"""
        # Сначала применяем стандартное форматирование
        formatted = super().format(record)
        
        # Затем маскируем ключи
        import re
        for pattern, replacer in self.KEY_PATTERNS:
            formatted = re.sub(pattern, replacer, formatted)
        
        return formatted


class ScannerLogger:
    """Улучшенная система логгирования для сканера"""
    
    def __init__(self, config: LoggingConfig, console: Optional[Console] = None):
        """
        Инициализация логгера
        
        Args:
            config: Конфигурация логгирования
            console: Console для Rich (опционально)
        """
        self.config = config
        self.console = console or Console()
        self.logger = logging.getLogger('scanner')
        self._setup_logging()
    
    def _setup_logging(self):
        """Настраивает систему логгирования"""
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Устанавливаем уровень
        level = getattr(logging, self.config.level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Создаем форматтер с маскировкой
        formatter = MaskedFormatter(self.config.format)
        
        # Обработчик для файла с ротацией
        if self.config.file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.file,
                maxBytes=self.config.max_size_mb * 1024 * 1024,  # MB to bytes
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Rich обработчик для консоли
        rich_handler = RichHandler(
            console=self.console,
            rich_tracebacks=True,
            show_path=False,
            show_time=False  # Время уже есть в формате
        )
        rich_handler.setFormatter(formatter)
        self.logger.addHandler(rich_handler)
        
        # Предотвращаем дублирование логов
        self.logger.propagate = False
    
    def info(self, message: str, **kwargs):
        """Логирует информационное сообщение"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Логирует предупреждение"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Логирует ошибку"""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Логирует отладочное сообщение"""
        self.logger.debug(message, **kwargs)
    
    def success(self, message: str):
        """Выводит сообщение об успехе"""
        self.console.print(f"✅ {message}", style="green")
        self.logger.info(f"SUCCESS: {message}")
    
    def failure(self, message: str):
        """Выводит сообщение об ошибке"""
        self.console.print(f"❌ {message}", style="red")
        self.logger.error(f"FAILURE: {message}")
    
    def progress_info(self, message: str):
        """Выводит информацию о прогрессе"""
        self.console.print(f"🔄 {message}", style="blue")
        self.logger.info(f"PROGRESS: {message}")
    
    def print_header(self, title: str, subtitle: str = None):
        """Выводит красивый заголовок"""
        text = Text(title, style="bold cyan")
        if subtitle:
            text.append(f"\n{subtitle}", style="dim")
        
        panel = Panel(text, expand=False, border_style="cyan")
        self.console.print(panel)
    
    def print_section(self, title: str):
        """Выводит заголовок секции"""
        self.console.print(f"\n📋 {title}", style="bold yellow")
        self.console.print("─" * (len(title) + 5), style="yellow")
    
    def print_stats_table(self, stats: dict, title: str = "Статистика"):
        """Выводит таблицу статистики"""
        table = Table(title=title)
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
        
        self.console.print(table)
    
    def create_progress_bar(self, description: str, total: int = None):
        """
        Создает прогресс-бар
        
        Args:
            description: Описание задачи
            total: Общее количество элементов (если известно)
            
        Returns:
            Progress: Объект прогресс-бара
        """
        if total:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeElapsedColumn(),
                console=self.console
            )
        else:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console
            )
        
        return progress
    
    def log_key_found(self, provider: str, masked_key: str, file_path: str):
        """Логирует найденный ключ"""
        self.success(f"{provider.upper()}: Найден валидный ключ {masked_key} в {file_path}")
    
    def log_key_invalid(self, provider: str, masked_key: str, reason: str = ""):
        """Логирует невалидный ключ"""
        reason_text = f" ({reason})" if reason else ""
        self.debug(f"{provider.upper()}: Ключ {masked_key} невалидный{reason_text}")
    
    def log_file_processed(self, file_path: str, keys_found: int):
        """Логирует обработанный файл"""
        if keys_found > 0:
            self.info(f"📄 Обработан файл {file_path}: найдено {keys_found} ключей")
        else:
            self.debug(f"📄 Обработан файл {file_path}: ключи не найдены")
    
    def log_cache_operation(self, operation: str, details: str = ""):
        """Логирует операции с кэшем"""
        self.debug(f"💾 Кэш: {operation} {details}")
    
    def log_rate_limit(self, api_type: str, remaining: int, reset_time: str = ""):
        """Логирует информацию о лимитах API"""
        if remaining < 10:
            self.warning(f"⚠️ Мало запросов {api_type} API: {remaining}")
        else:
            self.debug(f"📊 {api_type} API: осталось {remaining} запросов")
    
    def log_scan_summary(self, total_files: int, total_keys: int, valid_keys: int, scan_time: float):
        """Логирует итоговую статистику сканирования"""
        self.print_section("ИТОГИ СКАНИРОВАНИЯ")
        
        stats = {
            "Обработано файлов": total_files,
            "Найдено потенциальных ключей": total_keys,
            "Валидных ключей": valid_keys,
            "Время сканирования": f"{scan_time:.1f} сек",
            "Скорость": f"{total_files/scan_time:.1f} файлов/сек" if scan_time > 0 else "N/A"
        }
        
        self.print_stats_table(stats)
        
        if valid_keys > 0:
            self.success(f"Сканирование завершено! Найдено {valid_keys} валидных ключей")
        else:
            self.info("Сканирование завершено. Валидные ключи не найдены")


class ProgressTracker:
    """Трекер прогресса для асинхронных операций"""
    
    def __init__(self, logger: ScannerLogger):
        """
        Инициализация трекера прогресса
        
        Args:
            logger: Логгер для вывода сообщений
        """
        self.logger = logger
        self.progress = None
        self.tasks = {}
    
    def start_progress(self, description: str = "Обработка"):
        """Запускает отображение прогресса"""
        self.progress = self.logger.create_progress_bar(description)
        self.progress.start()
        return self.progress
    
    def add_task(self, task_id: str, description: str, total: int = None):
        """Добавляет задачу для отслеживания"""
        if self.progress:
            task = self.progress.add_task(description, total=total)
            self.tasks[task_id] = task
            return task
        return None
    
    def update_task(self, task_id: str, advance: int = 1, description: str = None):
        """Обновляет прогресс задачи"""
        if self.progress and task_id in self.tasks:
            kwargs = {'advance': advance}
            if description:
                kwargs['description'] = description
            
            self.progress.update(self.tasks[task_id], **kwargs)
    
    def complete_task(self, task_id: str):
        """Завершает задачу"""
        if self.progress and task_id in self.tasks:
            task = self.tasks[task_id]
            self.progress.update(task, completed=self.progress.tasks[task].total or 100)
    
    def stop_progress(self):
        """Останавливает отображение прогресса"""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.tasks.clear()