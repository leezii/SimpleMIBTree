"""Flask application configuration"""
import os

# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = os.path.join(project_root, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    TEMPLATES_FOLDER = os.path.join(project_root, 'templates')
    
    # Babel configuration
    LANGUAGES = ['en', 'zh']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(project_root, 'locales')
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'mib', 'txt', 'my', 'zip'}
    
    # Standard OID mapping table
    STANDARD_OID_MAP = {
        'iso': '1',
        'org': '1.3',
        'dod': '1.3.6',
        'internet': '1.3.6.1',
        'directory': '1.3.6.1.1',
        'mgmt': '1.3.6.1.2',
        'mib-2': '1.3.6.1.2.1',
        'experimental': '1.3.6.1.3',
        'private': '1.3.6.1.4',
        'enterprises': '1.3.6.1.4.1',
        'security': '1.3.6.1.5',
        'snmpV2': '1.3.6.1.6'
    }

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
