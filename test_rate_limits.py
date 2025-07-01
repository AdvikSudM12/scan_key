#!/usr/bin/env python3
"""
Тест проверки лимитов GitHub API
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импортируем класс сканера
from enhanced_scanner import EnhancedMultiProviderGitHubScanner

def test_rate_limits():
    """
    Тестирует функциональность проверки лимитов GitHub API
    """
    print("🧪 ТЕСТ ПРОВЕРКИ ЛИМИТОВ GITHUB API")
    print("="*60)
    
    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🔑 GitHub токен: {'✅ Найден' if github_token else '❌ Не найден'}")
    
    # Создаем экземпляр сканера
    scanner = EnhancedMultiProviderGitHubScanner(github_token)
    
    print(f"\n📊 ТЕСТ 1: Получение лимитов API")
    print("-" * 50)
    
    # Тестируем получение лимитов
    limits = scanner.check_rate_limits()
    
    if limits['status'] == 'success':
        print(f"✅ Успешно получены лимиты:")
        print(f"   🔎 Search API: {limits['search']['remaining']}/{limits['search']['limit']}")
        print(f"   🌐 Core API: {limits['core']['remaining']}/{limits['core']['limit']}")
        
        if limits['search']['reset_datetime']:
            print(f"   ⏰ Search сброс: {limits['search']['reset_datetime'].strftime('%H:%M:%S')}")
        if limits['core']['reset_datetime']:
            print(f"   ⏰ Core сброс: {limits['core']['reset_datetime'].strftime('%H:%M:%S')}")
    else:
        print(f"❌ Ошибка получения лимитов: {limits.get('error')}")
    
    print(f"\n📊 ТЕСТ 2: Вывод лимитов")
    print("-" * 50)
    
    # Тестируем вывод лимитов
    scanner.print_rate_limits()
    
    print(f"\n📊 ТЕСТ 3: Проверка возможности сканирования")
    print("-" * 50)
    
    # Тестируем проверку возможности продолжения
    can_continue = scanner.should_continue_scanning()
    print(f"Результат: {'✅ Можно продолжать' if can_continue else '❌ Нужно ждать'}")
    
    print(f"\n📊 ТЕСТ 4: Расчет использования API")
    print("-" * 50)
    
    if limits['status'] == 'success':
        search_used = limits['search']['limit'] - limits['search']['remaining']
        core_used = limits['core']['limit'] - limits['core']['remaining']
        
        search_percent = (search_used / limits['search']['limit']) * 100 if limits['search']['limit'] > 0 else 0
        core_percent = (core_used / limits['core']['limit']) * 100 if limits['core']['limit'] > 0 else 0
        
        print(f"🔎 Search API использовано: {search_used} ({search_percent:.1f}%)")
        print(f"🌐 Core API использовано: {core_used} ({core_percent:.1f}%)")
        
        # Оценка количества запросов для сканирования
        queries_count = len(scanner.get_search_queries())
        max_pages = 3
        estimated_search_requests = queries_count * max_pages  # Search API
        
        # Оценка Core API запросов (получение файлов)
        # Примерно 10-50 файлов на поисковый запрос
        avg_files_per_query = 25
        estimated_files = queries_count * avg_files_per_query
        estimated_core_requests = estimated_files  # Core API для получения содержимого файлов
        
        print(f"\n📈 ОЦЕНКА ДЛЯ СКАНИРОВАНИЯ:")
        print(f"   🔍 Планируемых поисковых запросов (Search API): ~{estimated_search_requests}")
        print(f"   � Ожидаемых файлов для обработки: ~{estimated_files}")
        print(f"   �📊 Планируемых запросов получения файлов (Core API): ~{estimated_core_requests}")
        print(f"   📊 Доступно Search API запросов: {limits['search']['remaining']}")
        print(f"   📊 Доступно Core API запросов: {limits['core']['remaining']}")
        
        # Проверяем лимиты для Search API
        if limits['search']['remaining'] >= estimated_search_requests:
            print(f"   ✅ Search API: Достаточно лимитов для поиска")
        else:
            possible_search_queries = limits['search']['remaining'] // max_pages
            print(f"   ⚠️  Search API: Хватит только на ~{possible_search_queries} поисковых запросов")
        
        # Проверяем лимиты для Core API
        if limits['core']['remaining'] >= estimated_core_requests:
            print(f"   ✅ Core API: Достаточно лимитов для получения файлов")
        else:
            possible_files = limits['core']['remaining']
            print(f"   ⚠️  Core API: Хватит только на ~{possible_files} файлов")
            
        # Общий вывод
        bottleneck = None
        if limits['search']['remaining'] < estimated_search_requests:
            bottleneck = f"Search API ({limits['search']['remaining']} из {estimated_search_requests})"
        elif limits['core']['remaining'] < estimated_core_requests:
            bottleneck = f"Core API ({limits['core']['remaining']} из {estimated_core_requests})"
            
        if bottleneck:
            print(f"   🛑 ОГРАНИЧЕНИЕ: {bottleneck}")
        else:
            print(f"   ✅ Достаточно лимитов для полного сканирования")
    
    print(f"\n🎉 ТЕСТ ЗАВЕРШЕН")

if __name__ == "__main__":
    test_rate_limits()
