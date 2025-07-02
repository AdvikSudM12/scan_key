"""
Тесты для нового архитектурного разделения модулей
"""

import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch

from validators import ValidatorFactory
from cache_manager import CacheManager
from github_client import GitHubClient


class TestValidatorFactory:
    """Тесты для фабрики валидаторов"""
    
    def test_supported_providers(self):
        """Тест поддерживаемых провайдеров"""
        providers = ValidatorFactory.get_supported_providers()
        assert 'openai' in providers
        assert 'anthropic' in providers
        assert 'google_gemini' in providers
    
    def test_create_validator(self):
        """Тест создания валидаторов"""
        openai_validator = ValidatorFactory.create_validator('openai')
        assert openai_validator is not None
        assert openai_validator.get_provider_name() == 'openai'
        
        anthropic_validator = ValidatorFactory.create_validator('anthropic')
        assert anthropic_validator is not None
        assert anthropic_validator.get_provider_name() == 'anthropic'
        
        google_validator = ValidatorFactory.create_validator('google_gemini')
        assert google_validator is not None
        assert google_validator.get_provider_name() == 'google_gemini'
        
        # Неизвестный провайдер
        unknown_validator = ValidatorFactory.create_validator('unknown')
        assert unknown_validator is None
    
    def test_identify_provider(self):
        """Тест идентификации провайдера"""
        # OpenAI
        assert ValidatorFactory.identify_provider('sk-1234567890abcdef') == 'openai'
        assert ValidatorFactory.identify_provider('sk-proj-1234567890') == 'openai'
        
        # Anthropic
        assert ValidatorFactory.identify_provider('sk-ant-api03-1234567890') == 'anthropic'
        assert ValidatorFactory.identify_provider('sk-ant-1234567890') == 'anthropic'
        
        # Google Gemini
        assert ValidatorFactory.identify_provider('AIzaSyD1234567890') == 'google_gemini'
        assert ValidatorFactory.identify_provider('AIzaBC1234567890') == 'google_gemini'
        
        # Неизвестный формат
        assert ValidatorFactory.identify_provider('unknown-key') is None
        assert ValidatorFactory.identify_provider('123456789') is None
    
    def test_key_masking(self):
        """Тест маскировки ключей"""
        validator = ValidatorFactory.create_validator('openai')
        
        # Обычный ключ
        masked = validator.mask_key('sk-1234567890abcdef1234567890abcdef12345678')
        assert masked.startswith('sk-1')
        assert masked.endswith('5678')
        assert '*' in masked
        
        # Короткий ключ
        short_masked = validator.mask_key('sk-12345')
        assert short_masked == '*' * 8  # Полная маскировка коротких ключей


class TestCacheManager:
    """Тесты для менеджера кэша"""
    
    def test_cache_initialization(self):
        """Тест инициализации кэша"""
        # Используем несуществующий файл
        cache_file = "/tmp/test_cache_" + str(os.getpid()) + ".json"
        
        try:
            cache = CacheManager(cache_file)
            stats = cache.get_stats()
            assert stats['processed_files'] == 0
            assert stats['tested_keys'] == 0
            assert not stats['cache_file_exists']
        finally:
            if os.path.exists(cache_file):
                os.unlink(cache_file)
    
    def test_file_processing_tracking(self):
        """Тест отслеживания обработанных файлов"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            cache_file = tmp.name
        
        try:
            cache = CacheManager(cache_file)
            
            file_id = "repo/owner:path/to/file.py:sha123"
            assert not cache.is_file_processed(file_id)
            
            cache.mark_file_processed(file_id)
            assert cache.is_file_processed(file_id)
            
            stats = cache.get_stats()
            assert stats['processed_files'] == 1
        finally:
            if os.path.exists(cache_file):
                os.unlink(cache_file)
    
    def test_key_testing_tracking(self):
        """Тест отслеживания протестированных ключей"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            cache_file = tmp.name
        
        try:
            cache = CacheManager(cache_file)
            
            api_key = "sk-1234567890abcdef1234567890abcdef12345678"
            assert not cache.is_key_tested(api_key)
            
            cache.mark_key_tested(api_key)
            assert cache.is_key_tested(api_key)
            
            stats = cache.get_stats()
            assert stats['tested_keys'] == 1
        finally:
            if os.path.exists(cache_file):
                os.unlink(cache_file)
    
    def test_cache_persistence(self):
        """Тест сохранения и загрузки кэша"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            cache_file = tmp.name
        
        try:
            # Создаем кэш и добавляем данные
            cache1 = CacheManager(cache_file)
            cache1.mark_file_processed("file1")
            cache1.mark_key_tested("sk-test123")
            cache1.save_cache()
            
            # Создаем новый экземпляр и проверяем загрузку
            cache2 = CacheManager(cache_file)
            assert cache2.is_file_processed("file1")
            assert cache2.is_key_tested("sk-test123")
            
            stats = cache2.get_stats()
            assert stats['processed_files'] == 1
            assert stats['tested_keys'] == 1
        finally:
            if os.path.exists(cache_file):
                os.unlink(cache_file)
    
    def test_key_masking_in_cache(self):
        """Тест маскировки ключей в кэше"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            cache_file = tmp.name
        
        try:
            cache = CacheManager(cache_file)
            api_key = "sk-1234567890abcdef1234567890abcdef12345678"
            
            cache.mark_key_tested(api_key)
            
            # Проверяем, что ключ не хранится в открытом виде
            cache.save_cache()
            
            with open(cache_file, 'r') as f:
                cache_content = f.read()
                # Полный ключ не должен быть в файле кэша
                assert api_key not in cache_content
                # Должна быть маскированная версия
                assert 'sk-1***5678' in cache_content
        finally:
            if os.path.exists(cache_file):
                os.unlink(cache_file)


class TestGitHubClient:
    """Тесты для клиента GitHub"""
    
    def test_client_initialization(self):
        """Тест инициализации клиента"""
        # Без токена
        client1 = GitHubClient()
        assert 'Authorization' not in client1.headers
        
        # С токеном
        client2 = GitHubClient('test_token')
        assert client2.headers['Authorization'] == 'token test_token'
    
    def test_search_queries_generation(self):
        """Тест генерации поисковых запросов"""
        client = GitHubClient()
        
        # Без недавних запросов
        queries_basic = client.get_search_queries(include_recent=False)
        assert len(queries_basic) > 0
        assert 'OPENAI_API_KEY' in queries_basic
        assert 'ANTHROPIC_API_KEY' in queries_basic
        assert 'GOOGLE_API_KEY' in queries_basic
        
        # С недавними запросами
        queries_with_recent = client.get_search_queries(include_recent=True)
        assert len(queries_with_recent) > len(queries_basic)
        
        # Проверяем наличие временных фильтров
        recent_queries = [q for q in queries_with_recent if 'pushed:>' in q]
        assert len(recent_queries) > 0
    
    @patch('requests.get')
    def test_rate_limits_check(self, mock_get):
        """Тест проверки лимитов API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'resources': {
                'search': {
                    'limit': 30,
                    'remaining': 25,
                    'reset': 1640995200  # Timestamp
                },
                'core': {
                    'limit': 5000,
                    'remaining': 4500,
                    'reset': 1640995200
                }
            }
        }
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        limits = client.check_rate_limits()
        
        assert limits['status'] == 'success'
        assert limits['search']['limit'] == 30
        assert limits['search']['remaining'] == 25
        assert limits['core']['limit'] == 5000
        assert limits['core']['remaining'] == 4500


if __name__ == '__main__':
    pytest.main([__file__, '-v'])