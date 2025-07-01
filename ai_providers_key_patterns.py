#!/usr/bin/env python3
"""
Форматы и паттерны API-ключей для различных AI-провайдеров
Собрано на основе официальной документации (декабрь 2024)
"""

import re
from typing import Dict, List, NamedTuple
from enum import Enum


class ProviderInfo(NamedTuple):
    """Информация о провайдере AI"""
    name: str
    patterns: List[re.Pattern]
    validation_url: str
    header_name: str
    description: str


class AIProvider(Enum):
    """Поддерживаемые AI провайдеры"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"


# Паттерны API-ключей для различных провайдеров
AI_PROVIDERS_PATTERNS = {
    AIProvider.OPENAI: ProviderInfo(
        name="OpenAI",
        patterns=[
            # Старый формат: sk- + 48 символов
            re.compile(r'sk-[A-Za-z0-9]{48}'),
            # Новый project формат: sk-proj- + 95-200 символов
            re.compile(r'sk-proj-[A-Za-z0-9\-_]{95,200}'),
            # Общий паттерн для любых sk- ключей
            re.compile(r'sk-[A-Za-z0-9\-_]{40,200}'),
            # Специфичный паттерн с T3BlbkFJ (base64 "OpenAI")
            re.compile(r'sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}'),
        ],
        validation_url="https://api.openai.com/v1/models",
        header_name="Authorization",  # Bearer TOKEN
        description="OpenAI API ключи начинаются с 'sk-' и могут иметь различные форматы"
    ),
    
    AIProvider.ANTHROPIC: ProviderInfo(
        name="Anthropic (Claude)",
        patterns=[
            # Основной формат: sk-ant-api03- + символы
            re.compile(r'sk-ant-api03-[A-Za-z0-9\-_]{95,200}'),
            # Общий паттерн для Anthropic
            re.compile(r'sk-ant-[A-Za-z0-9\-_]{40,200}'),
        ],
        validation_url="https://api.anthropic.com/v1/messages",
        header_name="x-api-key",
        description="Anthropic API ключи начинаются с 'sk-ant-' и имеют частичную подсказку вида 'sk-ant-api03-R2D...igAA'"
    ),
    
    AIProvider.GOOGLE_GEMINI: ProviderInfo(
        name="Google Gemini",
        patterns=[
            # API ключи Google обычно начинаются с AIza
            re.compile(r'AIza[A-Za-z0-9\-_]{35}'),
            # Альтернативный формат для Google API ключей
            re.compile(r'[A-Za-z0-9\-_]{39}'),  # 39 символов общий формат
        ],
        validation_url="https://generativelanguage.googleapis.com/v1/models",
        header_name="Authorization",  # Bearer TOKEN или x-goog-api-key
        description="Google Gemini API ключи обычно начинаются с 'AIza' и содержат 39 символов"
    )
}


def get_all_patterns() -> List[re.Pattern]:
    """
    Возвращает список всех паттернов для поиска API-ключей всех провайдеров
    
    Returns:
        List[re.Pattern]: Список скомпилированных регулярных выражений
    """
    all_patterns = []
    for provider_info in AI_PROVIDERS_PATTERNS.values():
        all_patterns.extend(provider_info.patterns)
    return all_patterns


def identify_provider(api_key: str) -> List[AIProvider]:
    """
    Определяет возможных провайдеров для данного API-ключа
    
    Args:
        api_key: API ключ для анализа
        
    Returns:
        List[AIProvider]: Список возможных провайдеров
    """
    matching_providers = []
    
    for provider, info in AI_PROVIDERS_PATTERNS.items():
        for pattern in info.patterns:
            if pattern.match(api_key):
                matching_providers.append(provider)
                break
    
    return matching_providers


def get_provider_info(provider: AIProvider) -> ProviderInfo:
    """
    Получает информацию о провайдере
    
    Args:
        provider: Провайдер AI
        
    Returns:
        ProviderInfo: Информация о провайдере
    """
    return AI_PROVIDERS_PATTERNS.get(provider)


def print_patterns_summary():
    """Выводит сводку всех паттернов"""
    print("🔍 Паттерны API-ключей для AI-провайдеров:")
    print("=" * 60)
    
    for provider, info in AI_PROVIDERS_PATTERNS.items():
        print(f"\n📡 {info.name} ({provider.value}):")
        print(f"   📋 Описание: {info.description}")
        print(f"   🔗 URL валидации: {info.validation_url}")
        print(f"   📝 Заголовок: {info.header_name}")
        print(f"   🔄 Паттерны ({len(info.patterns)}):")
        
        for i, pattern in enumerate(info.patterns, 1):
            print(f"      {i}. {pattern.pattern}")
    
    print(f"\n📊 Всего паттернов: {sum(len(info.patterns) for info in AI_PROVIDERS_PATTERNS.values())}")
    print("=" * 60)


if __name__ == "__main__":
    # Демонстрация работы
    print_patterns_summary()
    
    # Примеры тестирования
    test_keys = [
        "sk-1234567890abcdef1234567890abcdef12345678",  # OpenAI старый
        "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijk",  # OpenAI новый
        "sk-ant-api03-R2DabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789",  # Anthropic
        "AIzaSyDabcdefghijklmnopqrstuvwxyzABCDEFGH",  # Google Gemini
    ]
    
    print("\n🧪 Тестирование примеров ключей:")
    print("-" * 40)
    
    for key in test_keys:
        providers = identify_provider(key)
        if providers:
            provider_names = ", ".join([AI_PROVIDERS_PATTERNS[p].name for p in providers])
            print(f"✅ {key[:20]}... → {provider_names}")
        else:
            print(f"❌ {key[:20]}... → Не распознан")
