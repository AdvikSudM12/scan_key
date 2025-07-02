"""
Модуль для работы с GitHub API
"""

import asyncio
import aiohttp
import requests
import base64
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote


class GitHubClient:
    """Клиент для работы с GitHub API"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Инициализация GitHub клиента
        
        Args:
            github_token: Токен GitHub API для увеличения лимитов
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        
        # Настройка заголовков
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Enhanced-Multi-Provider-Scanner/3.0'
        }
        
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
    
    async def search_code_async(self, query: str, page: int = 1, per_page: int = 100) -> Dict:
        """
        Асинхронный поиск кода в GitHub
        
        Args:
            query: Поисковый запрос
            page: Номер страницы
            per_page: Количество результатов на страницу
            
        Returns:
            Dict: Результаты поиска
        """
        url = f"{self.base_url}/search/code"
        params = {
            'q': query,
            'page': page,
            'per_page': per_page,
            'sort': 'updated',
            'order': 'desc'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    # Rate limit exceeded
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    if reset_time:
                        reset_datetime = datetime.fromtimestamp(int(reset_time))
                        wait_time = (reset_datetime - datetime.now()).total_seconds()
                        if wait_time > 0:
                            print(f"⏰ Rate limit exceeded. Waiting {wait_time:.0f} seconds...")
                            await asyncio.sleep(wait_time + 1)
                            # Retry once
                            return await self.search_code_async(query, page, per_page)
                    
                    raise Exception(f"GitHub API rate limit exceeded")
                else:
                    raise Exception(f"GitHub API error: {response.status}")
    
    def search_code_sync(self, query: str, page: int = 1, per_page: int = 100) -> Dict:
        """
        Синхронный поиск кода в GitHub
        
        Args:
            query: Поисковый запрос
            page: Номер страницы
            per_page: Количество результатов на страницу
            
        Returns:
            Dict: Результаты поиска
        """
        url = f"{self.base_url}/search/code"
        params = {
            'q': query,
            'page': page,
            'per_page': per_page,
            'sort': 'updated',
            'order': 'desc'
        }
        
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            # Rate limit exceeded
            reset_time = response.headers.get('X-RateLimit-Reset')
            if reset_time:
                reset_datetime = datetime.fromtimestamp(int(reset_time))
                wait_time = (reset_datetime - datetime.now()).total_seconds()
                if wait_time > 0:
                    print(f"⏰ Rate limit exceeded. Waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time + 1)
                    # Retry once
                    return self.search_code_sync(query, page, per_page)
            
            raise Exception(f"GitHub API rate limit exceeded")
        else:
            raise Exception(f"GitHub API error: {response.status_code}")
    
    async def get_file_content_async(self, owner: str, repo: str, path: str, ref: str = None) -> Optional[str]:
        """
        Асинхронное получение содержимого файла
        
        Args:
            owner: Владелец репозитория
            repo: Имя репозитория
            path: Путь к файлу
            ref: Ветка или коммит (по умолчанию главная ветка)
            
        Returns:
            str: Содержимое файла или None в случае ошибки
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{quote(path)}"
        params = {}
        if ref:
            params['ref'] = ref
        
        timeout = aiohttp.ClientTimeout(total=15)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('encoding') == 'base64':
                            return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                    elif response.status == 403:
                        print(f"    ⚠️ Доступ запрещен к файлу: {path}")
                    elif response.status == 404:
                        print(f"    ⚠️ Файл не найден: {path}")
                    else:
                        print(f"    ⚠️ Ошибка загрузки файла {path}: {response.status}")
        except Exception as e:
            print(f"    ⚠️ Исключение при загрузке файла {path}: {e}")
        
        return None
    
    def get_file_content_sync(self, owner: str, repo: str, path: str, ref: str = None) -> Optional[str]:
        """
        Синхронное получение содержимого файла
        
        Args:
            owner: Владелец репозитория
            repo: Имя репозитория
            path: Путь к файлу
            ref: Ветка или коммит (по умолчанию главная ветка)
            
        Returns:
            str: Содержимое файла или None в случае ошибки
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{quote(path)}"
        params = {}
        if ref:
            params['ref'] = ref
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('encoding') == 'base64':
                    return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            elif response.status_code == 403:
                print(f"    ⚠️ Доступ запрещен к файлу: {path}")
            elif response.status_code == 404:
                print(f"    ⚠️ Файл не найден: {path}")
            else:
                print(f"    ⚠️ Ошибка загрузки файла {path}: {response.status_code}")
        except Exception as e:
            print(f"    ⚠️ Исключение при загрузке файла {path}: {e}")
        
        return None
    
    def check_rate_limits(self) -> Dict:
        """
        Проверяет текущие лимиты GitHub API
        
        Returns:
            Dict: Информация о лимитах
        """
        try:
            url = f"{self.base_url}/rate_limit"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'search': {
                        'limit': data['resources']['search']['limit'],
                        'remaining': data['resources']['search']['remaining'],
                        'reset_time': data['resources']['search']['reset'],
                        'reset_datetime': datetime.fromtimestamp(data['resources']['search']['reset'])
                    },
                    'core': {
                        'limit': data['resources']['core']['limit'],
                        'remaining': data['resources']['core']['remaining'],
                        'reset_time': data['resources']['core']['reset'],
                        'reset_datetime': datetime.fromtimestamp(data['resources']['core']['reset'])
                    },
                    'status': 'success'
                }
            else:
                return {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_search_queries(self, include_recent: bool = True) -> List[str]:
        """
        Генерирует список поисковых запросов для разных провайдеров
        
        Args:
            include_recent: Включать ли запросы по недавно обновленным репозиториям
            
        Returns:
            List[str]: Список поисковых запросов
        """
        base_queries = [
            # OpenAI patterns
            'OPENAI_API_KEY',
            'sk- AND openai',
            'openai.api_key',
            'openai_api_key',
            'sk- AND gpt',
            'OpenAI-Api-Key',
            'sk- language:python',
            'sk- language:javascript',
            'sk- language:typescript',
            'sk- extension:py',
            'sk- extension:js',
            'sk- extension:ts',
            'sk- extension:env',
            'sk- extension:yaml',
            'sk- extension:json',
            'sk- path:config',
            'sk- path:env',
            'sk- filename:.env',
            'sk- filename:config',
            
            # Anthropic patterns
            'ANTHROPIC_API_KEY',
            'CLAUDE_API_KEY',
            'sk-ant',
            'anthropic AND api_key',
            'claude AND api_key',
            'sk-ant- language:python',
            'sk-ant- extension:py',
            'sk-ant- extension:env',
            'ANTHROPIC_API_KEY extension:env',
            'claude_api_key',
            'anthropic_key',
            'sk-ant- filename:.env',
            'sk-ant- path:config',
            'anthropic AND key',
            'claude AND key',
            'sk-ant- extension:yaml',
            'sk-ant- extension:json',
            
            # Google Gemini patterns
            'GOOGLE_API_KEY',
            'GEMINI_API_KEY',
            'AIza',
            'google AND api_key AND gemini',
            'generative AND ai AND key',
            'AIza language:python',
            'AIza extension:py',
            'AIza extension:env',
            'GOOGLE_API_KEY extension:env',
            'gemini_api_key',
            'google_ai_key',
            'AIza filename:.env',
            'AIza path:config',
            'google AND gemini AND key',
            'generativelanguage AND key',
            'AIza extension:yaml',
            'AIza extension:json'
        ]
        
        if include_recent:
            # Добавляем запросы для недавно обновленных репозиториев
            recent_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            recent_queries = [
                # OpenAI
                f'sk- pushed:>{recent_date}',
                f'OPENAI_API_KEY created:>{recent_date}',
                f'openai api_key updated:>{recent_date}',
                # Anthropic
                f'sk-ant pushed:>{recent_date}',
                f'ANTHROPIC_API_KEY created:>{recent_date}',
                f'anthropic api_key updated:>{recent_date}',
                # Google
                f'AIza pushed:>{recent_date}',
                f'GOOGLE_API_KEY created:>{recent_date}',
                f'gemini api_key updated:>{recent_date}',
            ]
            base_queries.extend(recent_queries)
        
        return base_queries