"""Flask application main file"""
import os
import logging
from flask import Flask
from config import config
from routes import main_bp
from i18n import init_babel

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__, 
                template_folder=config[config_name].TEMPLATES_FOLDER)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize internationalization support
    init_babel(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Flask application started, environment: {config_name}")
    
    # Register blueprint
    app.register_blueprint(main_bp)
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
