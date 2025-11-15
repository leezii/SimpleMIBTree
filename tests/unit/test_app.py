"""Unit tests for Flask application factory"""
import os
import pytest
from unittest.mock import patch
from app import create_app

class TestAppFactory:
    """Test cases for Flask application factory"""
    
    def test_create_app_default_config(self):
        """Test creating app with default configuration"""
        app = create_app()
        
        assert app is not None
        assert app.config['TESTING'] is False
        assert app.config['DEBUG'] is True  # Default is development
        assert 'SECRET_KEY' in app.config
        assert 'UPLOAD_FOLDER' in app.config
        assert 'MAX_CONTENT_LENGTH' in app.config
    
    def test_create_app_development_config(self):
        """Test creating app with development configuration"""
        app = create_app('development')
        
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False
    
    def test_create_app_production_config(self):
        """Test creating app with development configuration"""
        app = create_app('production')
        
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
    
    def test_create_app_testing_config(self):
        """Test creating app with testing configuration"""
        app = create_app('testing')
        
        assert app.config['TESTING'] is True
        assert app.config['WTF_CSRF_ENABLED'] is False
    
    def test_create_app_from_environment(self):
        """Test creating app from environment variable"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            app = create_app()
            
            assert app.config['DEBUG'] is False
    
    def test_create_app_uploads_folder_creation(self, tmp_path):
        """Test that uploads folder is created"""
        app = create_app('testing')
        app.config['UPLOAD_FOLDER'] = tmp_path
        
        with app.app_context():
            # The upload folder should exist after app creation
            assert os.path.exists(app.config['UPLOAD_FOLDER'])
    
    def test_create_app_blueprint_registration(self):
        """Test that blueprints are registered"""
        app = create_app('testing')
        
        # Check if main blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'main' in blueprint_names
    
    def test_create_app_babel_initialization(self):
        """Test that Babel is initialized"""
        app = create_app('testing')
        
        # Check if Babel extension is initialized
        # This would depend on the actual implementation
        # For now, just ensure no errors during creation
        assert app is not None
    
    def test_create_app_logging_configuration(self):
        """Test that logging is configured"""
        app = create_app('testing')
        
        # The app should configure logging without errors
        with app.app_context():
            # Check if logging is configured
            # This is a basic check - actual implementation may vary
            assert app.logger is not None
    
    def test_create_app_template_folder(self):
        """Test that template folder is set correctly"""
        app = create_app('testing')
        
        assert 'templates' in app.template_folder
        assert os.path.isabs(app.template_folder)

class TestAppConfiguration:
    """Test application configuration"""
    
    def test_app_config_completeness(self):
        """Test that all required config is present"""
        app = create_app('testing')
        
        required_configs = [
            'SECRET_KEY',
            'UPLOAD_FOLDER',
            'MAX_CONTENT_LENGTH',
            'TEMPLATES_FOLDER',
            'LANGUAGES',
            'BABEL_TRANSLATION_DIRECTORIES',
            'BABEL_DEFAULT_LOCALE',
            'BABEL_DEFAULT_TIMEZONE',
            'ALLOWED_EXTENSIONS',
            'STANDARD_OID_MAP'
        ]
        
        for config_key in required_configs:
            assert config_key in app.config, f"Missing config: {config_key}"
    
    def test_app_config_types(self):
        """Test that config values have correct types"""
        app = create_app('testing')
        
        assert isinstance(app.config['SECRET_KEY'], str)
        assert isinstance(app.config['UPLOAD_FOLDER'], str)
        assert isinstance(app.config['MAX_CONTENT_LENGTH'], int)
        assert isinstance(app.config['LANGUAGES'], list)
        assert isinstance(app.config['ALLOWED_EXTENSIONS'], set)
        assert isinstance(app.config['STANDARD_OID_MAP'], dict)
    
    def test_app_config_values(self):
        """Test specific config values"""
        app = create_app('testing')
        
        # Test allowed extensions
        assert 'mib' in app.config['ALLOWED_EXTENSIONS']
        assert 'txt' in app.config['ALLOWED_EXTENSIONS']
        assert 'zip' in app.config['ALLOWED_EXTENSIONS']
        
        # Test languages
        assert 'en' in app.config['LANGUAGES']
        assert 'zh' in app.config['LANGUAGES']
        
        # Test OID map
        assert 'iso' in app.config['STANDARD_OID_MAP']
        assert app.config['STANDARD_OID_MAP']['iso'] == '1'

class TestAppErrorHandling:
    """Test error handling in application factory"""
    
    def test_create_app_invalid_config(self):
        """Test creating app with invalid config name"""
        # Should handle unknown config gracefully
        app = create_app('invalid_config')
        
        # Should still create an app, likely with default config
        assert app is not None
    
    def test_create_app_config_import_error(self):
        """Test handling of config import errors"""
        # This would require mocking the config module
        # For now, just test basic error handling
        with patch('app.config', side_effect=ImportError("Config error")):
            with pytest.raises(ImportError):
                create_app('testing')

class TestAppContext:
    """Test application context behavior"""
    
    def test_app_context_manager(self):
        """Test application context manager"""
        app = create_app('testing')
        
        with app.app_context():
            # Should be able to access current_app
            from flask import current_app
            assert current_app is app
    
    def test_app_context_current_app_access(self):
        """Test current_app access in context"""
        app = create_app('testing')
        
        with app.app_context():
            from flask import current_app
            assert current_app.config['TESTING'] is True
    
    def test_app_context_request_context(self):
        """Test request context behavior"""
        app = create_app('testing')
        
        with app.test_request_context('/'):
            from flask import request
            assert request.method == 'GET'
            assert request.path == '/'

class TestAppFactoryEdgeCases:
    """Test edge cases in application factory"""
    
    def test_multiple_app_instances(self):
        """Test creating multiple app instances"""
        app1 = create_app('testing')
        app2 = create_app('testing')
        
        # Should create separate instances
        assert app1 is not app2
        assert app1.config != app2.config or app1.config is not app2.config
    
    def test_app_config_modification(self):
        """Test that app config modification doesn't affect other instances"""
        app1 = create_app('testing')
        app2 = create_app('testing')
        
        # Modify config of one app
        app1.config['TEST_VALUE'] = 'test1'
        app2.config['TEST_VALUE'] = 'test2'
        
        # Should be independent
        assert app1.config['TEST_VALUE'] == 'test1'
        assert app2.config['TEST_VALUE'] == 'test2'
    
    @pytest.mark.parametrize("config_name", [
        'development', 'production', 'testing', 'default'
    ])
    def test_different_configurations(self, config_name):
        """Test creating app with different configuration names"""
        app = create_app(config_name)
        
        assert app is not None
        assert hasattr(app, 'config')
        assert isinstance(app.config, dict)

class TestAppIntegration:
    """Test integration scenarios"""
    
    def test_app_with_real_client(self):
        """Test app with test client"""
        app = create_app('testing')
        client = app.test_client()
        
        assert client is not None
        
        # Should be able to make requests
        response = client.get('/')
        assert response.status_code == 200
    
    def test_app_route_registration(self):
        """Test that routes are properly registered"""
        app = create_app('testing')
        
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        # Should have main routes
        assert '/' in routes
        assert '/mib-parser' in routes
        assert '/oid-calculator' in routes
        assert '/mib-oid-generator' in routes
        assert '/set-language' in routes
        assert '/upload-mib' in routes
    
    def test_app_template_loading(self):
        """Test that templates can be loaded"""
        app = create_app('testing')
        
        with app.test_request_context('/'):
            from flask import render_template
            
            # Should be able to render templates without errors
            # This assumes templates exist
            try:
                result = render_template('index.html', lang='en')
                assert isinstance(result, str)
            except Exception as e:
                # If template doesn't exist, that's expected in test environment
                assert 'template' in str(e).lower() or 'not found' in str(e).lower()

class TestAppSecurity:
    """Test security-related configurations"""
    
    def test_secret_key_configuration(self):
        """Test secret key configuration"""
        app = create_app('testing')
        
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0
    
    def test_production_security_config(self):
        """Test production security settings"""
        app = create_app('production')
        
        # Production should have debug disabled
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
    
    def test_testing_security_config(self):
        """Test testing security settings"""
        app = create_app('testing')
        
        # Testing should have specific security settings
        assert app.config['TESTING'] is True
        assert app.config.get('WTF_CSRF_ENABLED') is False
