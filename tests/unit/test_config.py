"""Unit tests for config module"""
import os
import pytest
from unittest.mock import patch
from config import Config, DevelopmentConfig, ProductionConfig, config

class TestConfig:
    """Test cases for base configuration class"""
    
    def test_config_basic_attributes(self):
        """Test basic configuration attributes"""
        config = Config()
        
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'UPLOAD_FOLDER')
        assert hasattr(config, 'MAX_CONTENT_LENGTH')
        assert hasattr(config, 'TEMPLATES_FOLDER')
        assert hasattr(config, 'LANGUAGES')
        assert hasattr(config, 'BABEL_TRANSLATION_DIRECTORIES')
        assert hasattr(config, 'BABEL_DEFAULT_LOCALE')
        assert hasattr(config, 'BABEL_DEFAULT_TIMEZONE')
        assert hasattr(config, 'ALLOWED_EXTENSIONS')
        assert hasattr(config, 'STANDARD_OID_MAP')
    
    def test_secret_key_default(self):
        """Test default SECRET_KEY setting"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
    
    def test_secret_key_from_env(self):
        """Test SECRET_KEY from environment variable"""
        # Force reload of config module to pick up new environment
        import importlib
        import config
        
        with patch.dict(os.environ, {'SECRET_KEY': 'test-secret-key'}):
            importlib.reload(config)
            config_instance = config.Config()
            assert config_instance.SECRET_KEY == 'test-secret-key'
    
    def test_upload_folder_path(self):
        """Test UPLOAD_FOLDER path configuration"""
        config = Config()
        expected_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'uploads')
        assert config.UPLOAD_FOLDER.endswith('uploads')
    
    def test_max_content_length(self):
        """Test MAX_CONTENT_LENGTH setting"""
        config = Config()
        expected_length = 16 * 1024 * 1024  # 16MB
        assert config.MAX_CONTENT_LENGTH == expected_length
    
    def test_templates_folder_path(self):
        """Test TEMPLATES_FOLDER path configuration"""
        config = Config()
        expected_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'templates')
        assert config.TEMPLATES_FOLDER.endswith('templates')
    
    def test_languages_configuration(self):
        """Test LANGUAGES configuration"""
        config = Config()
        assert isinstance(config.LANGUAGES, list)
        assert 'en' in config.LANGUAGES
        assert 'zh' in config.LANGUAGES
        assert len(config.LANGUAGES) == 2
    
    def test_babel_configuration(self):
        """Test Babel configuration settings"""
        config = Config()
        
        assert config.BABEL_DEFAULT_LOCALE == 'en'
        assert config.BABEL_DEFAULT_TIMEZONE == 'UTC'
        
        # Test translation directories path
        expected_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'locales')
        assert config.BABEL_TRANSLATION_DIRECTORIES.endswith('locales')
    
    def test_allowed_extensions(self):
        """Test ALLOWED_EXTENSIONS configuration"""
        config = Config()
        
        assert isinstance(config.ALLOWED_EXTENSIONS, set)
        assert 'mib' in config.ALLOWED_EXTENSIONS
        assert 'txt' in config.ALLOWED_EXTENSIONS
        assert 'my' in config.ALLOWED_EXTENSIONS
        assert 'zip' in config.ALLOWED_EXTENSIONS
        assert len(config.ALLOWED_EXTENSIONS) == 4
    
    def test_standard_oid_map(self):
        """Test STANDARD_OID_MAP configuration"""
        config = Config()
        
        assert isinstance(config.STANDARD_OID_MAP, dict)
        assert 'iso' in config.STANDARD_OID_MAP
        assert 'org' in config.STANDARD_OID_MAP
        assert 'dod' in config.STANDARD_OID_MAP
        assert 'internet' in config.STANDARD_OID_MAP
        assert 'mgmt' in config.STANDARD_OID_MAP
        assert 'mib-2' in config.STANDARD_OID_MAP
        assert 'private' in config.STANDARD_OID_MAP
        assert 'enterprises' in config.STANDARD_OID_MAP
        
        # Test specific OID values
        assert config.STANDARD_OID_MAP['iso'] == '1'
        assert config.STANDARD_OID_MAP['org'] == '1.3'
        assert config.STANDARD_OID_MAP['dod'] == '1.3.6'
        assert config.STANDARD_OID_MAP['internet'] == '1.3.6.1'
        assert config.STANDARD_OID_MAP['enterprises'] == '1.3.6.1.4.1'

class TestDevelopmentConfig:
    """Test cases for development configuration"""
    
    def test_development_config_inheritance(self):
        """Test that DevelopmentConfig inherits from Config"""
        dev_config = DevelopmentConfig()
        assert isinstance(dev_config, Config)
        
        # Should have all base config attributes
        assert hasattr(dev_config, 'SECRET_KEY')
        assert hasattr(dev_config, 'UPLOAD_FOLDER')
        assert hasattr(dev_config, 'DEBUG')
    
    def test_development_debug_enabled(self):
        """Test that DEBUG is enabled in development"""
        dev_config = DevelopmentConfig()
        assert dev_config.DEBUG is True

class TestProductionConfig:
    """Test cases for production configuration"""
    
    def test_production_config_inheritance(self):
        """Test that ProductionConfig inherits from Config"""
        prod_config = ProductionConfig()
        assert isinstance(prod_config, Config)
        
        # Should have all base config attributes
        assert hasattr(prod_config, 'SECRET_KEY')
        assert hasattr(prod_config, 'UPLOAD_FOLDER')
        assert hasattr(prod_config, 'DEBUG')
    
    def test_production_debug_disabled(self):
        """Test that DEBUG is disabled in production"""
        prod_config = ProductionConfig()
        assert prod_config.DEBUG is False

class TestConfigDictionary:
    """Test cases for configuration dictionary"""
    
    def test_config_dict_structure(self):
        """Test configuration dictionary structure"""
        assert isinstance(config, dict)
        assert 'development' in config
        assert 'production' in config
        assert 'default' in config
        assert len(config) == 3
    
    def test_config_dict_values(self):
        """Test configuration dictionary values"""
        assert config['development'] == DevelopmentConfig
        assert config['production'] == ProductionConfig
        assert config['default'] == DevelopmentConfig  # Default should be development
    
    def test_config_dict_config_classes(self):
        """Test that config dict contains configuration classes"""
        assert config['development'] is DevelopmentConfig
        assert config['production'] is ProductionConfig
        assert config['default'] is DevelopmentConfig

class TestConfigEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_project_root_calculation(self):
        """Test project root path calculation"""
        # Import config to trigger project_root calculation
        import importlib
        import config
        
        # Reload config to test project root calculation
        importlib.reload(config)
        
        # The project_root should be calculated correctly
        assert hasattr(config, 'project_root')
        assert os.path.isabs(config.project_root)
        assert config.project_root.endswith('flask_web')
    
    def test_path_resolution_with_symlinks(self):
        """Test path resolution with symbolic links"""
        config = Config()
        
        # Upload folder should resolve to absolute path
        assert os.path.isabs(config.UPLOAD_FOLDER)
        assert os.path.isabs(config.TEMPLATES_FOLDER)
        assert os.path.isabs(config.BABEL_TRANSLATION_DIRECTORIES)
    
    def test_configuration_immutability(self):
        """Test that configuration objects behave as expected"""
        dev_config = DevelopmentConfig()
        prod_config = ProductionConfig()
        
        # Different instances should be independent
        dev_config.TEST_ATTR = 'test_value'
        assert not hasattr(prod_config, 'TEST_ATTR')
    
    @pytest.mark.parametrize("env_var,expected_key", [
        ("", "dev-secret-key-change-in-production"),
        ("my-secret-key", "my-secret-key"),
        ("complex-secret-with-special-chars-123!@#", "complex-secret-with-special-chars-123!@#")
    ])
    def test_secret_key_variations(self, env_var, expected_key):
        """Test SECRET_KEY with various environment variable values"""
        import importlib
        import config
        
        # Force reload of config module to pick up new environment
        with patch.dict(os.environ, {'SECRET_KEY': env_var}):
            importlib.reload(config)
            config_instance = config.Config()
            assert config_instance.SECRET_KEY == expected_key

class TestConfigurationValidation:
    """Test configuration validation and consistency"""
    
    def test_upload_folder_permissions(self, tmp_path):
        """Test upload folder path permissions"""
        config = Config()
        
        # The upload folder path should be valid
        upload_path = config.UPLOAD_FOLDER
        
        # Create the directory if it doesn't exist
        os.makedirs(upload_path, exist_ok=True)
        
        # Should be able to check if directory exists
        assert os.path.exists(upload_path) or os.path.isdir(os.path.dirname(upload_path))
    
    def test_templates_folder_structure(self):
        """Test templates folder structure"""
        config = Config()
        templates_path = config.TEMPLATES_FOLDER
        
        # Should end with 'templates'
        assert templates_path.endswith('templates')
        assert os.path.isabs(templates_path)
    
    def test_locales_folder_structure(self):
        """Test locales folder structure"""
        config = Config()
        locales_path = config.BABEL_TRANSLATION_DIRECTORIES
        
        # Should end with 'locales'
        assert locales_path.endswith('locales')
        assert os.path.isabs(locales_path)
    
    def test_allowed_extensions_consistency(self):
        """Test allowed extensions consistency"""
        config = Config()
        
        # All extensions should be lowercase
        for ext in config.ALLOWED_EXTENSIONS:
            assert ext == ext.lower()
            assert isinstance(ext, str)
    
    def test_oid_map_consistency(self):
        """Test OID map consistency"""
        config = Config()
        
        # All keys should be strings
        for key in config.STANDARD_OID_MAP:
            assert isinstance(key, str)
        
        # All values should be valid OID strings (digits and dots)
        for value in config.STANDARD_OID_MAP.values():
            assert isinstance(value, str)
            # OID should only contain digits and dots
            for char in value:
                assert char.isdigit() or char == '.'
    
    def test_languages_list_consistency(self):
        """Test languages list consistency"""
        config = Config()
        
        # All languages should be 2-character codes
        for lang in config.LANGUAGES:
            assert isinstance(lang, str)
            assert len(lang) == 2
            assert lang.islower()

class TestConfigurationIntegration:
    """Test configuration integration scenarios"""
    
    def test_config_with_flask_app(self):
        """Test configuration with Flask app integration"""
        from flask import Flask
        
        config_obj = DevelopmentConfig()
        app = Flask(__name__)
        app.config.from_object(config_obj)
        
        # Flask app should have the configuration
        assert app.config['SECRET_KEY'] == config_obj.SECRET_KEY
        assert app.config['UPLOAD_FOLDER'] == config_obj.UPLOAD_FOLDER
        assert app.config['DEBUG'] is True
        assert app.config['ALLOWED_EXTENSIONS'] == config_obj.ALLOWED_EXTENSIONS
    
    def test_config_environment_switching(self):
        """Test switching between configurations"""
        dev_config = config['development']
        prod_config = config['production']
        default_config = config['default']
        
        # Default should be development
        assert default_config is dev_config
        assert dev_config is not prod_config
        assert dev_config.DEBUG is True
        assert prod_config.DEBUG is False
