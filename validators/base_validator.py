"""
Базовый класс для всех валидаторов API ключей
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseValidator(ABC):
    """Базовый абстрактный класс для валидации API ключей"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    @abstractmethod
    async def validate_async(self, api_key: str) -> bool:
        """
        Асинхронная валидация API ключа
        
        Args:
            api_key: API ключ для валидации
            
        Returns:
            bool: True если ключ валидный
        """
        pass
    
    @abstractmethod
    def validate_sync(self, api_key: str) -> bool:
        """
        Синхронная валидация API ключа (для backward compatibility)
        
        Args:
            api_key: API ключ для валидации
            
        Returns:
            bool: True если ключ валидный
        """
        pass
    
    def mask_key(self, api_key: str) -> str:
        """
        Маскирует API ключ для безопасного логгирования
        
        Args:
            api_key: API ключ для маскировки
            
        Returns:
            str: Маскированный ключ
        """
        if len(api_key) <= 8:
            return "*" * len(api_key)
        
        # Показываем первые 4 и последние 4 символа
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
    
    def get_provider_name(self) -> str:
        """Возвращает имя провайдера"""
        return self.provider_name