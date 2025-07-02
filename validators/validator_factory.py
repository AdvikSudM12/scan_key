"""
Фабрика для создания валидаторов API ключей
"""

from typing import Optional
from .base_validator import BaseValidator
from .openai_validator import OpenAIValidator
from .anthropic_validator import AnthropicValidator
from .google_gemini_validator import GoogleGeminiValidator


class ValidatorFactory:
    """Фабрика для создания валидаторов разных провайдеров"""
    
    _validators = {
        'openai': OpenAIValidator,
        'anthropic': AnthropicValidator,
        'google_gemini': GoogleGeminiValidator
    }
    
    @classmethod
    def create_validator(cls, provider: str) -> Optional[BaseValidator]:
        """
        Создает валидатор для указанного провайдера
        
        Args:
            provider: Имя провайдера ('openai', 'anthropic', 'google_gemini')
            
        Returns:
            BaseValidator: Экземпляр валидатора или None если провайдер не найден
        """
        validator_class = cls._validators.get(provider.lower())
        if validator_class:
            return validator_class()
        return None
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Возвращает список поддерживаемых провайдеров"""
        return list(cls._validators.keys())
    
    @classmethod
    def identify_provider(cls, api_key: str) -> Optional[str]:
        """
        Определяет провайдера по формату API ключа
        
        Args:
            api_key: API ключ для анализа
            
        Returns:
            str: Имя провайдера или None если не удалось определить
        """
        api_key = api_key.strip()
        
        # OpenAI ключи
        if api_key.startswith('sk-'):
            if 'ant-' in api_key:
                return 'anthropic'
            return 'openai'
        
        # Google Gemini ключи
        if api_key.startswith('AIza'):
            return 'google_gemini'
        
        return None