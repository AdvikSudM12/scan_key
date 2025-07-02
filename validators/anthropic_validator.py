"""
Валидатор API ключей Anthropic (Claude)
"""

import asyncio
import aiohttp
import requests
from .base_validator import BaseValidator


class AnthropicValidator(BaseValidator):
    """Валидатор для API ключей Anthropic"""
    
    def __init__(self):
        super().__init__("anthropic")
    
    async def validate_async(self, api_key: str) -> bool:
        """
        Асинхронная валидация API ключа Anthropic
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                }
                
                # Тестовый запрос к API Anthropic
                data = {
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'test'}]
                }
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=data,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False
                    elif response.status == 429:  # Rate limit
                        print(f"    Ключ валидный, но есть ограничения по скорости")
                        return True
                    elif response.status == 403:  # Forbidden - возможно нет доступа к модели
                        print(f"    Ключ валидный, но нет доступа к модели")
                        return True
                    else:
                        print(f"    Неожиданный статус Anthropic API: {response.status}")
                        return False
                        
        except Exception as e:
            error_str = str(e).lower()
            if any(err in error_str for err in ['invalid api key', 'unauthorized']):
                return False
            elif any(err in error_str for err in ['quota', 'rate limit', 'billing']):
                print(f"    Ключ валидный, но есть ограничения: {error_str}")
                return True
            else:
                print(f"    Ошибка валидации Anthropic: {error_str}")
                return False
    
    def validate_sync(self, api_key: str) -> bool:
        """
        Синхронная валидация API ключа Anthropic
        """
        try:
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            # Тестовый запрос к API Anthropic
            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 1,
                'messages': [{'role': 'user', 'content': 'test'}]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                return False
            elif response.status_code == 429:  # Rate limit
                print(f"    Ключ валидный, но есть ограничения по скорости")
                return True
            elif response.status_code == 403:  # Forbidden
                print(f"    Ключ валидный, но нет доступа к модели")
                return True
            else:
                print(f"    Неожиданный статус Anthropic API: {response.status_code}")
                return False
                
        except Exception as e:
            error_str = str(e).lower()
            if any(err in error_str for err in ['invalid api key', 'unauthorized']):
                return False
            elif any(err in error_str for err in ['quota', 'rate limit', 'billing']):
                print(f"    Ключ валидный, но есть ограничения: {error_str}")
                return True
            else:
                print(f"    Ошибка валидации Anthropic: {error_str}")
                return False