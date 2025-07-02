"""
Валидатор API ключей OpenAI
"""

import asyncio
import aiohttp
from openai import OpenAI
from .base_validator import BaseValidator


class OpenAIValidator(BaseValidator):
    """Валидатор для API ключей OpenAI"""
    
    def __init__(self):
        super().__init__("openai")
    
    async def validate_async(self, api_key: str) -> bool:
        """
        Асинхронная валидация API ключа OpenAI
        """
        try:
            # Используем синхронный OpenAI клиент в потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._validate_openai_sync, 
                api_key
            )
            return result
        except Exception as e:
            error_str = str(e).lower()
            if any(err in error_str for err in ['invalid api key', 'invalid_api_key', 'unauthorized', 'incorrect api key']):
                return False
            elif any(err in error_str for err in ['quota', 'rate limit', 'billing']):
                print(f"    Ключ валидный, но есть ограничения: {error_str}")
                return True
            else:
                print(f"    Неизвестная ошибка OpenAI: {error_str}")
                return False
    
    def validate_sync(self, api_key: str) -> bool:
        """
        Синхронная валидация API ключа OpenAI
        """
        return self._validate_openai_sync(api_key)
    
    def _validate_openai_sync(self, api_key: str) -> bool:
        """
        Внутренний метод синхронной валидации
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
                print(f"    Неизвестная ошибка OpenAI: {error_str}")
                
        return False