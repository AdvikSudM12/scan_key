"""
Валидатор API ключей Google Gemini
"""

import asyncio
import aiohttp
import requests
from .base_validator import BaseValidator


class GoogleGeminiValidator(BaseValidator):
    """Валидатор для API ключей Google Gemini"""
    
    def __init__(self):
        super().__init__("google_gemini")
    
    async def validate_async(self, api_key: str) -> bool:
        """
        Асинхронная валидация API ключа Google Gemini
        """
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Проверяем что есть модели в ответе
                        return 'models' in data and len(data.get('models', [])) > 0
                    elif response.status == 403:
                        # Возможно ключ валиден, но нет доступа к конкретному API
                        print(f"    Google API возвратил 403 - возможно валидный ключ без прав доступа")
                        return True
                    elif response.status == 401:
                        return False
                    elif response.status in [429, 503]:  # Rate limit
                        print(f"    Ключ валидный, но есть ограничения: {response.status}")
                        return True
                    else:
                        print(f"    Неожиданный статус Google API: {response.status}")
                        return False
                        
        except Exception as e:
            error_str = str(e).lower()
            if any(err in error_str for err in ['invalid api key', 'unauthorized']):
                return False
            elif any(err in error_str for err in ['quota', 'rate limit', 'billing']):
                print(f"    Ключ валидный, но есть ограничения: {error_str}")
                return True
            else:
                print(f"    Ошибка валидации Google: {error_str}")
                return False
    
    def validate_sync(self, api_key: str) -> bool:
        """
        Синхронная валидация API ключа Google Gemini
        """
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Проверяем что есть модели в ответе
                return 'models' in data and len(data.get('models', [])) > 0
            elif response.status_code == 403:
                # Возможно ключ валиден, но нет доступа к конкретному API
                print(f"    Google API возвратил 403 - возможно валидный ключ без прав доступа")
                return True
            elif response.status_code == 401:
                return False
            elif response.status_code in [429, 503]:  # Rate limit
                print(f"    Ключ валидный, но есть ограничения: {response.status_code}")
                return True
            else:
                print(f"    Неожиданный статус Google API: {response.status_code}")
                return False
                
        except Exception as e:
            error_str = str(e).lower()
            if any(err in error_str for err in ['invalid api key', 'unauthorized']):
                return False
            elif any(err in error_str for err in ['quota', 'rate limit', 'billing']):
                print(f"    Ключ валидный, но есть ограничения: {error_str}")
                return True
            else:
                print(f"    Ошибка валидации Google: {error_str}")
                return False