#!/usr/bin/env python3
"""
Тестовый скрипт для проверки мульти-провайдерного сканера
"""

import os
import json
from dotenv import load_dotenv
from enhanced_scanner import EnhancedMultiProviderGitHubScanner
from ai_providers_key_patterns import AI_PROVIDERS_PATTERNS, get_all_patterns

# Загружаем переменные окружения
load_dotenv()


def test_pattern_identification():
    """Тестирует идентификацию провайдеров по паттернам ключей"""
    print("🧪 Тестирование идентификации провайдеров")
    print("=" * 50)
    
    # Создаем сканер для тестирования
    scanner = EnhancedMultiProviderGitHubScanner()
    
    # Тестовые ключи для каждого провайдера
    test_keys = {
        'openai': [
            'sk-1234567890abcdef1234567890abcdef12345678',  # Старый формат
            'sk-proj-abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijk',  # Новый
            'sk-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',  # Общий
        ],
        'anthropic': [
            'sk-ant-api03-R2DabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789',
            'sk-ant-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        ],
        'google_gemini': [
            'AIzaSyDabcdefghijklmnopqrstuvwxyzABCDEFGH',
            'AIzaBCdefghijklmnopqrstuvwxyz1234567890ABC',
        ]
    }
    
    all_correct = True
    
    for expected_provider, keys in test_keys.items():
        print(f"\n🤖 Тестирование {expected_provider.upper()}:")
        for i, key in enumerate(keys, 1):
            identified = scanner.identify_provider(key)
            if identified == expected_provider:
                print(f"   ✅ Ключ {i}: {key[:20]}... → {identified}")
            else:
                print(f"   ❌ Ключ {i}: {key[:20]}... → {identified} (ожидалось: {expected_provider})")
                all_correct = False
    
    print(f"\n📊 Результат: {'✅ Все тесты прошли' if all_correct else '❌ Есть ошибки'}")
    return all_correct


def test_key_extraction():
    """Тестирует извлечение ключей из различных форматов контента"""
    print("\n🧪 Тестирование извлечения ключей")
    print("=" * 50)
    
    scanner = EnhancedMultiProviderGitHubScanner()
    
    # Тестовый контент с ключами разных провайдеров
    test_content = '''
    # OpenAI configuration
    OPENAI_API_KEY=sk-1234567890abcdef1234567890abcdef12345678
    openai.api_key = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijk"
    
    # Anthropic configuration
    ANTHROPIC_API_KEY="sk-ant-api03-R2DabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    claude_key = sk-ant-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    
    # Google Gemini configuration
    GOOGLE_API_KEY=AIzaSyDabcdefghijklmnopqrstuvwxyzABCDEFGH
    google_ai_key: "AIzaBCdefghijklmnopqrstuvwxyz1234567890ABC"
    
    # В JSON
    {
        "api_keys": {
            "openai": "sk-testkey1234567890abcdef1234567890abcdef123",
            "anthropic": "sk-ant-testkey1234567890abcdef1234567890abcdef123456789",
            "google": "AIzaTestKey1234567890abcdef1234567890ABC"
        }
    }
    '''
    
    extracted_keys = scanner.extract_api_keys(test_content)
    print(f"🔑 Извлечено ключей: {len(extracted_keys)}")
    
    # Проверяем каждый извлеченный ключ
    provider_counts = {'openai': 0, 'anthropic': 0, 'google_gemini': 0, 'unknown': 0}
    
    for key in extracted_keys:
        provider = scanner.identify_provider(key)
        if provider:
            provider_counts[provider] += 1
            print(f"   ✅ {provider.upper()}: {key[:20]}...")
        else:
            provider_counts['unknown'] += 1
            print(f"   ❓ НЕИЗВЕСТНЫЙ: {key[:20]}...")
    
    print(f"\n📊 Статистика по провайдерам:")
    for provider, count in provider_counts.items():
        if count > 0:
            print(f"   {provider.upper()}: {count} ключей")
    
    return len(extracted_keys) > 0


def test_file_structure():
    """Тестирует создание файлов для каждого провайдера"""
    print("\n🧪 Тестирование файловой структуры")
    print("=" * 50)
    
    scanner = EnhancedMultiProviderGitHubScanner()
    
    # Проверяем что файлы создались
    for provider, filename in scanner.valid_keys_files.items():
        if os.path.exists(filename):
            print(f"   ✅ {provider.upper()}: {filename}")
            
            # Проверяем структуру файла
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'scan_info' in data and 'valid_keys' in data:
                    print(f"      📄 Структура корректна")
                    print(f"      🔑 Ключей: {len(data['valid_keys'])}")
                else:
                    print(f"      ❌ Некорректная структура")
            except Exception as e:
                print(f"      ❌ Ошибка чтения: {e}")
        else:
            print(f"   ❌ {provider.upper()}: Файл не создан")
    
    return True


def test_search_queries():
    """Тестирует генерацию поисковых запросов"""
    print("\n🧪 Тестирование поисковых запросов")
    print("=" * 50)
    
    scanner = EnhancedMultiProviderGitHubScanner()
    queries = scanner.get_search_queries(include_recent=False)
    
    # Проверяем что есть запросы для каждого провайдера
    openai_queries = [q for q in queries if any(term in q.lower() for term in ['openai', 'sk-'])]
    anthropic_queries = [q for q in queries if any(term in q.lower() for term in ['anthropic', 'claude', 'sk-ant'])]
    google_queries = [q for q in queries if any(term in q.lower() for term in ['google', 'gemini', 'aiza'])]
    
    print(f"📊 Всего запросов: {len(queries)}")
    print(f"   🤖 OpenAI: {len(openai_queries)} запросов")
    print(f"   🤖 Anthropic: {len(anthropic_queries)} запросов")  
    print(f"   🤖 Google: {len(google_queries)} запросов")
    
    print(f"\n📝 Примеры запросов:")
    for provider, provider_queries in [('OpenAI', openai_queries[:3]), ('Anthropic', anthropic_queries[:2]), ('Google', google_queries[:2])]:
        print(f"   {provider}:")
        for query in provider_queries:
            print(f"      - {query}")
    
    return len(queries) > 0


def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ МУЛЬТИ-ПРОВАЙДЕРНОГО СКАНЕРА")
    print("👨‍💻 Автор: PRIZRAKJJ | Telegram: t.me/SafeVibeCode")
    print("=" * 70)
    
    tests = [
        ("Идентификация провайдеров", test_pattern_identification),
        ("Извлечение ключей", test_key_extraction),
        ("Файловая структура", test_file_structure),
        ("Поисковые запросы", test_search_queries),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛЕН"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Результат: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты успешно пройдены! Сканер готов к работе.")
    else:
        print("⚠️ Некоторые тесты провалены. Требуется доработка.")


if __name__ == "__main__":
    main()
