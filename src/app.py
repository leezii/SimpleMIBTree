"""Flask 应用主文件"""
import os
import logging
from flask import Flask
from config import config
from routes import main_bp

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__, 
                template_folder=config[config_name].TEMPLATES_FOLDER)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Flask 应用已启动，环境: {config_name}")
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
