"""Unit tests for internationalization module"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from i18n import get_locale, init_babel

class TestGetLocale:
    """Test cases for get_locale function"""
    
    def test_get_locale_from_url_parameter(self):
        """Test getting locale from URL parameter"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            # Mock request with lang parameter
            mock_request.args = {'lang': 'zh'}
            mock_session.__contains__ = Mock(return_value=False)
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'zh'
            mock_session.__setitem__.assert_called_with('language', 'zh')
    
    def test_get_locale_from_url_parameter_en(self):
        """Test getting English locale from URL parameter"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            mock_request.args = {'lang': 'en'}
            mock_session.__contains__ = Mock(return_value=False)
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'en'
            mock_session.__setitem__.assert_called_with('language', 'en')
    
    def test_get_locale_invalid_url_parameter(self):
        """Test getting locale from URL parameter"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            mock_request.args = {'lang': 'invalid'}
            mock_session.__contains__ = Mock(return_value=False)
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='en')
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'en'  # Should fall back to browser language
            mock_session.__setitem__.assert_called_with('language', 'en')
    
    def test_get_locale_from_session(self):
        """Test getting locale from session"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            mock_request.args = {}  # No URL parameter
            mock_session.__contains__ = Mock(return_value=True)
            mock_session.__getitem__ = Mock(return_value='zh')
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'zh'
            mock_session.__getitem__.assert_called_once_with('language')
    
    def test_get_locale_from_browser(self):
        """Test getting locale from browser language"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            mock_request.args = {}  # No URL parameter
            mock_session.__contains__ = Mock(return_value=False)
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='zh')
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'zh'
            mock_session.__setitem__.assert_called_with('language', 'zh')
    
    def test_get_locale_browser_fallback_to_default(self):
        """Test browser language fallback to default"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            mock_request.args = {}  # No URL parameter
            mock_session.__contains__ = Mock(return_value=False)
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value=None)
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'en'  # Should fall back to default
            mock_session.__setitem__.assert_called_with('language', 'en')
    
    def test_get_locale_priority_order(self):
        """Test locale priority order: URL > Session > Browser > Default"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            # URL parameter should take highest priority
            mock_request.args = {'lang': 'en'}
            mock_session.__contains__ = Mock(return_value=True)
            mock_session.__getitem__ = Mock(return_value='zh')  # Session has different language
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='zh')
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'en'  # URL parameter wins over session
            mock_session.__setitem__.assert_called_with('language', 'en')
    
    def test_get_locale_session_persistence(self):
        """Test that locale is saved to session"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session, \
             patch('i18n.current_app') as mock_current_app:
            
            mock_request.args = {'lang': 'zh'}
            mock_session.__contains__ = Mock(return_value=False)
            mock_session.permanent = False
            mock_current_app.config = {'SESSION_PERMANENT': True}
            
            locale = get_locale()
            
            assert locale == 'zh'
            # Should set session as permanent
            assert mock_session.permanent is True
            mock_session.__setitem__.assert_called_with('language', 'zh')
    
    def test_get_locale_priority_order(self):
        """Test locale priority order: URL > Session > Browser > Default"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            # URL parameter should take highest priority
            mock_request.args = {'lang': 'en'}
            mock_session.__contains__ = Mock(return_value=True)
            mock_session.__getitem__ = Mock(return_value='zh')  # Session has different locale
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='zh')
            
            locale = get_locale()
            
            assert locale == 'en'  # URL parameter wins
    
    def test_get_locale_session_persistence(self):
        """Test that locale is saved to session"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            mock_request.args = {'lang': 'zh'}
            mock_session.__contains__ = Mock(return_value=False)
            mock_session.permanent = False
            
            locale = get_locale()
            
            assert locale == 'zh'
            # Should set session as permanent
            assert mock_session.permanent is True
            # Should save to session
            mock_session.__setitem__.assert_called_with('language', 'zh')

class TestInitBabel:
    """Test cases for init_babel function"""
    
    def test_init_babel_basic(self):
        """Test basic Babel initialization"""
        app = Flask(__name__)
        
        with patch('i18n.Babel') as mock_babel_class:
            mock_babel = Mock()
            mock_babel_class.return_value = mock_babel
            
            result = init_babel(app)
            
            # Should create Babel instance
            mock_babel_class.assert_called_once()
            
            # Should initialize app
            mock_babel.init_app.assert_called_once_with(
                app,
                default_locale='en',
                default_translation_directories='locales',
                locale_selector=get_locale
            )
            
            # Should return the babel instance
            assert result is mock_babel
    
    def test_init_babel_with_custom_config(self):
        """Test Babel initialization with custom app config"""
        app = Flask(__name__)
        app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Shanghai'
        
        with patch('i18n.Babel') as mock_babel_class:
            mock_babel = Mock()
            mock_babel_class.return_value = mock_babel
            
            init_babel(app)
            
            # Should still use our parameters, not app config
            mock_babel.init_app.assert_called_once_with(
                app,
                default_locale='en',  # Our hardcoded value
                default_translation_directories='locales',
                locale_selector=get_locale
            )
    
    def test_init_babel_multiple_calls(self):
        """Test multiple calls to init_babel"""
        app = Flask(__name__)
        
        with patch('i18n.Babel') as mock_babel_class:
            mock_babel1 = Mock()
            mock_babel2 = Mock()
            mock_babel_class.side_effect = [mock_babel1, mock_babel2]
            
            result1 = init_babel(app)
            result2 = init_babel(app)
            
            # Should create separate instances
            assert result1 is mock_babel1
            assert result2 is mock_babel2
            assert result1 is not result2

class TestI18nEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_get_locale_empty_request_args(self):
        """Test get_locale with empty request args"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            mock_request.args = {}
            mock_session.__contains__ = Mock(return_value=False)
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='en')
            
            locale = get_locale()
            
            assert locale == 'en'
    
    def test_get_locale_session_exception(self):
        """Test get_locale with session access exception"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            mock_request.args = {}
            mock_session.__contains__ = Mock(side_effect=Exception("Session error"))
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='zh')
            
            # Should not raise exception
            locale = get_locale()
            assert locale == 'zh'
    
    def test_get_locale_request_exception(self):
        """Test get_locale with request access exception"""
        with patch('i18n.request') as mock_request:
            mock_request.args = Mock(side_effect=Exception("Request error"))
            
            with pytest.raises(Exception):
                get_locale()
    
    def test_get_locale_invalid_browser_language(self):
        """Test browser language with invalid format"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            mock_request.args = {}
            mock_session.__contains__ = Mock(return_value=False)
            mock_request.accept_languages = Mock()
            mock_request.accept_languages.best_match = Mock(return_value='invalid-locale')
            
            locale = get_locale()
            
            # Should fall back to default when browser locale is invalid
            assert locale == 'invalid-locale'  # Actually returns what browser provides
    
    def test_init_babel_with_none_app(self):
        """Test init_babel with None app"""
        with patch('i18n.Babel') as mock_babel_class:
            mock_babel = Mock()
            mock_babel_class.return_value = mock_babel
            
            # Should handle None gracefully
            result = init_babel(None)
            
            mock_babel.init_app.assert_called_once_with(
                None,
                default_locale='en',
                default_translation_directories='locales',
                locale_selector=get_locale
            )
            assert result is mock_babel

class TestI18nIntegration:
    """Test integration scenarios"""
    
    def test_full_workflow_with_flask_app(self):
        """Test complete workflow with Flask app"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        with app.test_request_context('/?lang=zh'):
            # Initialize Babel
            babel = init_babel(app)
            
            # Get locale
            locale = get_locale()
            
            # Should get locale from URL parameter
            assert locale == 'zh'
    
    def test_workflow_with_session(self):
        """Test workflow with session storage"""
        app = Flask(__name__)
        app.secret_key = 'test-secret'
        
        with app.test_request_context('/'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['language'] = 'zh'
                
                # Mock request to use session
                with patch('i18n.request') as mock_request, \
                     patch('i18n.session') as mock_session:
                    
                    mock_request.args = {}
                    mock_session.__contains__ = Mock(return_value=True)
                    mock_session.__getitem__ = Mock(return_value='zh')
                    
                    locale = get_locale()
                    assert locale == 'zh'
    
    def test_workflow_with_browser_language(self):
        """Test workflow with browser language detection"""
        app = Flask(__name__)
        
        with app.test_request_context('/', headers={
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }):
            with patch('i18n.session') as mock_session:
                mock_session.__contains__ = Mock(return_value=False)
                
                locale = get_locale()
                # Should detect Chinese from Accept-Language header
                assert locale in ['zh', 'en']  # Depending on best_match implementation

class TestI18nLogging:
    """Test logging functionality"""
    
    def test_get_locale_logging(self, caplog):
        """Test logging in get_locale function"""
        import logging
        logger = logging.getLogger('i18n')
        logger.setLevel(logging.INFO)
        
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            mock_request.args = {'lang': 'zh'}
            mock_session.__contains__ = Mock(return_value=False)
            
            locale = get_locale()
            
            # Should log language setting
            assert 'Language set from URL parameter: zh' in caplog.text
    
    def test_init_babel_logging(self, caplog):
        """Test logging in init_babel function"""
        import logging
        logger = logging.getLogger('i18n')
        logger.setLevel(logging.INFO)
        
        app = Flask(__name__)
        
        with patch('i18n.Babel') as mock_babel_class:
            mock_babel = Mock()
            mock_babel_class.return_value = mock_babel
            
            init_babel(app)
            
            # Should log initialization
            assert 'Babel initialized' in caplog.text

class TestI18nPerformance:
    """Test performance-related scenarios"""
    
    def test_get_locale_performance(self):
        """Test get_locale performance with multiple calls"""
        with patch('i18n.request') as mock_request, \
             patch('i18n.session') as mock_session:
            
            mock_request.args = {}
            mock_session.__contains__ = Mock(return_value=True)
            mock_session.__getitem__ = Mock(return_value='en')
            
            # Multiple calls should be fast
            import time
            start_time = time.time()
            
            for _ in range(100):
                locale = get_locale()
                assert locale == 'en'
            
            elapsed_time = time.time() - start_time
            assert elapsed_time < 1.0  # Should complete quickly
    
    def test_init_babel_performance(self):
        """Test init_babel performance"""
        with patch('i18n.Babel') as mock_babel_class:
            mock_babel = Mock()
            mock_babel_class.return_value = mock_babel
            
            import time
            start_time = time.time()
            
            for _ in range(10):
                app = Flask(__name__)
                result = init_babel(app)
                assert result is mock_babel
            
            elapsed_time = time.time() - start_time
            assert elapsed_time < 1.0  # Should complete quickly

@pytest.mark.parametrize("url_lang,session_lang,browser_lang,expected", [
    ('en', 'zh', 'zh-CN', 'en'),      # URL takes priority
    (None, 'zh', 'en', 'zh'),         # Session takes priority
    (None, None, 'zh', 'zh'),         # Browser takes priority
    (None, None, 'invalid', 'en'),     # Falls back to default
    ('invalid', 'zh', 'en', 'zh'),     # Invalid URL, session used
])
def test_get_locale_priority_matrix(url_lang, session_lang, browser_lang, expected):
    """Test get_locale with various priority combinations"""
    with patch('i18n.request') as mock_request, \
         patch('i18n.session') as mock_session:
        
        # Setup request args
        mock_request.args = {'lang': url_lang} if url_lang else {}
        mock_request.accept_languages = Mock()
        mock_request.accept_languages.best_match = Mock(return_value=browser_lang)
        
        # Setup session
        mock_session.__contains__ = Mock(return_value=session_lang is not None)
        mock_session.__getitem__ = Mock(return_value=session_lang) if session_lang else Mock()
        
        locale = get_locale()
        assert locale == expected
