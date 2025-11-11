"""Flask 应用配置"""
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = os.path.join(project_root, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    TEMPLATES_FOLDER = os.path.join(project_root, 'templates')
    
    # Babel 配置
    LANGUAGES = ['zh', 'en']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(project_root, 'locales')
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'mib', 'txt', 'my', 'zip'}
    
    # 标准 OID 映射表
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
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
