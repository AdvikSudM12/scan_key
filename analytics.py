"""
Модуль аналитики и статистики для сканера API ключей
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ScanSession:
    """Данные одной сессии сканирования"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_files_processed: int = 0
    total_keys_found: int = 0
    valid_keys_found: int = 0
    queries_executed: int = 0
    api_calls_made: int = 0
    errors_encountered: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    providers_stats: Dict[str, Dict[str, int]] = None
    top_repositories: List[Dict[str, Any]] = None
    scan_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.providers_stats is None:
            self.providers_stats = defaultdict(lambda: {'keys_found': 0, 'valid_keys': 0})
        if self.top_repositories is None:
            self.top_repositories = []
    
    @property
    def duration_seconds(self) -> float:
        """Возвращает продолжительность сканирования в секундах"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    @property
    def files_per_second(self) -> float:
        """Возвращает скорость обработки файлов в секунду"""
        duration = self.duration_seconds
        return self.total_files_processed / duration if duration > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        """Возвращает долю валидных ключей от общего количества найденных"""
        return (self.valid_keys_found / self.total_keys_found * 100) if self.total_keys_found > 0 else 0.0


class AnalyticsManager:
    """Менеджер аналитики и статистики"""
    
    def __init__(self, analytics_file: str = 'scanner_analytics.json'):
        """
        Инициализация менеджера аналитики
        
        Args:
            analytics_file: Файл для хранения данных аналитики
        """
        self.analytics_file = analytics_file
        self.current_session: Optional[ScanSession] = None
        self.session_history: List[ScanSession] = []
        
        # Счетчики для текущей сессии
        self.repositories_counter = Counter()
        self.file_extensions_counter = Counter()
        self.error_types_counter = Counter()
        self.hourly_activity = defaultdict(int)
        
        self._load_analytics()
    
    def start_session(self, session_id: str = None, config: Dict[str, Any] = None) -> str:
        """
        Начинает новую сессию сканирования
        
        Args:
            session_id: Идентификатор сессии (если не указан, генерируется автоматически)
            config: Конфигурация сканирования
            
        Returns:
            str: Идентификатор сессии
        """
        if session_id is None:
            session_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = ScanSession(
            session_id=session_id,
            start_time=datetime.now(),
            scan_config=config
        )
        
        # Сбрасываем счетчики
        self.repositories_counter.clear()
        self.file_extensions_counter.clear()
        self.error_types_counter.clear()
        self.hourly_activity.clear()
        
        return session_id
    
    def end_session(self):
        """Завершает текущую сессию сканирования"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            
            # Сохраняем топ репозиториев
            self.current_session.top_repositories = [
                {'repository': repo, 'files_found': count}
                for repo, count in self.repositories_counter.most_common(10)
            ]
            
            # Сохраняем сессию в историю
            self.session_history.append(self.current_session)
            
            # Сохраняем аналитику
            self._save_analytics()
            
            self.current_session = None
    
    def record_file_processed(self, file_path: str, repository: str, keys_found: int = 0):
        """
        Записывает обработку файла
        
        Args:
            file_path: Путь к файлу
            repository: Репозиторий
            keys_found: Количество найденных ключей
        """
        if not self.current_session:
            return
        
        self.current_session.total_files_processed += 1
        self.current_session.total_keys_found += keys_found
        
        # Обновляем счетчики
        self.repositories_counter[repository] += 1
        
        # Извлекаем расширение файла
        file_ext = Path(file_path).suffix.lower()
        if file_ext:
            self.file_extensions_counter[file_ext] += 1
        
        # Записываем активность по часам
        current_hour = datetime.now().hour
        self.hourly_activity[current_hour] += 1
    
    def record_valid_key(self, provider: str, repository: str):
        """
        Записывает найденный валидный ключ
        
        Args:
            provider: Провайдер API ключа
            repository: Репозиторий где найден ключ
        """
        if not self.current_session:
            return
        
        self.current_session.valid_keys_found += 1
        self.current_session.providers_stats[provider]['valid_keys'] += 1
    
    def record_key_found(self, provider: str):
        """
        Записывает найденный потенциальный ключ
        
        Args:
            provider: Провайдер API ключа
        """
        if not self.current_session:
            return
        
        self.current_session.providers_stats[provider]['keys_found'] += 1
    
    def record_query_executed(self):
        """Записывает выполненный поисковый запрос"""
        if self.current_session:
            self.current_session.queries_executed += 1
    
    def record_api_call(self):
        """Записывает API вызов"""
        if self.current_session:
            self.current_session.api_calls_made += 1
    
    def record_error(self, error_type: str, error_message: str = ""):
        """
        Записывает ошибку
        
        Args:
            error_type: Тип ошибки
            error_message: Сообщение об ошибке
        """
        if self.current_session:
            self.current_session.errors_encountered += 1
        
        self.error_types_counter[error_type] += 1
    
    def record_cache_hit(self):
        """Записывает попадание в кэш"""
        if self.current_session:
            self.current_session.cache_hits += 1
    
    def record_cache_miss(self):
        """Записывает промах кэша"""
        if self.current_session:
            self.current_session.cache_misses += 1
    
    def get_current_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику текущей сессии
        
        Returns:
            Dict: Статистика текущей сессии
        """
        if not self.current_session:
            return {}
        
        cache_total = self.current_session.cache_hits + self.current_session.cache_misses
        cache_hit_rate = (self.current_session.cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            'session_id': self.current_session.session_id,
            'duration': f"{self.current_session.duration_seconds:.1f} сек",
            'files_processed': self.current_session.total_files_processed,
            'keys_found': self.current_session.total_keys_found,
            'valid_keys': self.current_session.valid_keys_found,
            'success_rate': f"{self.current_session.success_rate:.1f}%",
            'speed': f"{self.current_session.files_per_second:.1f} файлов/сек",
            'queries_executed': self.current_session.queries_executed,
            'api_calls': self.current_session.api_calls_made,
            'errors': self.current_session.errors_encountered,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'providers': dict(self.current_session.providers_stats),
            'top_repositories': self.repositories_counter.most_common(5),
            'file_extensions': self.file_extensions_counter.most_common(5)
        }
    
    def get_historical_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Возвращает историческую статистику
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Dict: Историческая статистика
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_sessions = [
            session for session in self.session_history
            if session.start_time >= cutoff_date
        ]
        
        if not recent_sessions:
            return {}
        
        total_files = sum(s.total_files_processed for s in recent_sessions)
        total_keys = sum(s.total_keys_found for s in recent_sessions)
        total_valid = sum(s.valid_keys_found for s in recent_sessions)
        total_duration = sum(s.duration_seconds for s in recent_sessions)
        
        # Собираем статистику по провайдерам
        providers_aggregated = defaultdict(lambda: {'keys_found': 0, 'valid_keys': 0})
        for session in recent_sessions:
            for provider, stats in session.providers_stats.items():
                providers_aggregated[provider]['keys_found'] += stats['keys_found']
                providers_aggregated[provider]['valid_keys'] += stats['valid_keys']
        
        # Топ репозитории за период
        all_repositories = Counter()
        for session in recent_sessions:
            for repo_info in session.top_repositories:
                all_repositories[repo_info['repository']] += repo_info['files_found']
        
        return {
            'period_days': days,
            'total_sessions': len(recent_sessions),
            'total_files_processed': total_files,
            'total_keys_found': total_keys,
            'total_valid_keys': total_valid,
            'overall_success_rate': f"{(total_valid / total_keys * 100) if total_keys > 0 else 0:.1f}%",
            'average_speed': f"{total_files / total_duration if total_duration > 0 else 0:.1f} файлов/сек",
            'total_scan_time': f"{total_duration / 3600:.1f} часов",
            'providers_stats': dict(providers_aggregated),
            'top_repositories': all_repositories.most_common(10),
            'sessions_per_day': f"{len(recent_sessions) / days:.1f}",
            'average_files_per_session': f"{total_files / len(recent_sessions):.0f}" if recent_sessions else "0"
        }
    
    def get_trends_analysis(self) -> Dict[str, Any]:
        """
        Анализирует тренды в данных
        
        Returns:
            Dict: Анализ трендов
        """
        if len(self.session_history) < 2:
            return {}
        
        # Сравниваем последние 7 дней с предыдущими 7 днями
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        recent_week = [s for s in self.session_history if s.start_time >= week_ago]
        previous_week = [s for s in self.session_history if two_weeks_ago <= s.start_time < week_ago]
        
        if not recent_week or not previous_week:
            return {}
        
        recent_speed = sum(s.files_per_second for s in recent_week) / len(recent_week)
        previous_speed = sum(s.files_per_second for s in previous_week) / len(previous_week)
        
        recent_success = sum(s.success_rate for s in recent_week) / len(recent_week)
        previous_success = sum(s.success_rate for s in previous_week) / len(previous_week)
        
        speed_change = ((recent_speed - previous_speed) / previous_speed * 100) if previous_speed > 0 else 0
        success_change = recent_success - previous_success
        
        return {
            'speed_trend': {
                'current_week_avg': f"{recent_speed:.1f} файлов/сек",
                'previous_week_avg': f"{previous_speed:.1f} файлов/сек",
                'change_percent': f"{speed_change:+.1f}%",
                'trend': 'улучшение' if speed_change > 0 else 'ухудшение' if speed_change < 0 else 'стабильно'
            },
            'success_rate_trend': {
                'current_week_avg': f"{recent_success:.1f}%",
                'previous_week_avg': f"{previous_success:.1f}%",
                'change_percent': f"{success_change:+.1f}%",
                'trend': 'улучшение' if success_change > 0 else 'ухудшение' if success_change < 0 else 'стабильно'
            }
        }
    
    def _load_analytics(self):
        """Загружает данные аналитики из файла"""
        try:
            if os.path.exists(self.analytics_file):
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Восстанавливаем историю сессий
                for session_data in data.get('sessions', []):
                    session = ScanSession(
                        session_id=session_data['session_id'],
                        start_time=datetime.fromisoformat(session_data['start_time']),
                        end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
                        total_files_processed=session_data.get('total_files_processed', 0),
                        total_keys_found=session_data.get('total_keys_found', 0),
                        valid_keys_found=session_data.get('valid_keys_found', 0),
                        queries_executed=session_data.get('queries_executed', 0),
                        api_calls_made=session_data.get('api_calls_made', 0),
                        errors_encountered=session_data.get('errors_encountered', 0),
                        cache_hits=session_data.get('cache_hits', 0),
                        cache_misses=session_data.get('cache_misses', 0),
                        providers_stats=session_data.get('providers_stats', {}),
                        top_repositories=session_data.get('top_repositories', []),
                        scan_config=session_data.get('scan_config', {})
                    )
                    self.session_history.append(session)
                
        except Exception as e:
            print(f"⚠️ Ошибка загрузки аналитики: {e}")
    
    def _save_analytics(self):
        """Сохраняет данные аналитики в файл"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'sessions': []
            }
            
            # Сохраняем все сессии
            for session in self.session_history:
                session_data = {
                    'session_id': session.session_id,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat() if session.end_time else None,
                    'total_files_processed': session.total_files_processed,
                    'total_keys_found': session.total_keys_found,
                    'valid_keys_found': session.valid_keys_found,
                    'queries_executed': session.queries_executed,
                    'api_calls_made': session.api_calls_made,
                    'errors_encountered': session.errors_encountered,
                    'cache_hits': session.cache_hits,
                    'cache_misses': session.cache_misses,
                    'providers_stats': dict(session.providers_stats),
                    'top_repositories': session.top_repositories,
                    'scan_config': session.scan_config
                }
                data['sessions'].append(session_data)
            
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Ошибка сохранения аналитики: {e}")
    
    def export_report(self, file_path: str, days: int = 30):
        """
        Экспортирует отчет в файл
        
        Args:
            file_path: Путь для сохранения отчета
            days: Количество дней для включения в отчет
        """
        stats = self.get_historical_stats(days)
        trends = self.get_trends_analysis()
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'period_days': days,
            'historical_stats': stats,
            'trends_analysis': trends,
            'current_session': self.get_current_stats() if self.current_session else None
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Отчет экспортирован в {file_path}")
        except Exception as e:
            print(f"⚠️ Ошибка экспорта отчета: {e}")