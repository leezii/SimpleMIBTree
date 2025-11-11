"""国际化支持模块"""
from flask_babel import Babel
from flask import request, session
import logging

logger = logging.getLogger(__name__)

def get_locale():
    """获取用户语言偏好"""
    # 1. Check language setting in URL parameters
    lang = request.args.get('lang')
    if lang in ['zh', 'en']:
        logger.info(f"Language set from URL parameter: {lang}")
        session['language'] = lang  # Save to session
        session.permanent = True  # Make session persistent
        return lang
    
    # 2. Check language setting in session
    if 'language' in session:
        session_lang = session['language']
        logger.info(f"Language retrieved from session: {session_lang}")
        return session_lang
    
    # 3. Check browser language setting
    browser_lang = request.accept_languages.best_match(['zh', 'en']) or 'zh'
    logger.info(f"Using browser language: {browser_lang}")
    session['language'] = browser_lang  # Save to session
    session.permanent = True  # Make session persistent
    return browser_lang

def init_babel(app):
    """初始化Babel国际化支持"""
    # Flask-Babel 3.x 使用新的方式设置语言选择器
    # 通过 init_app 的 locale_selector 参数设置
    babel = Babel()
    
    # 初始化应用并设置语言选择器
    babel.init_app(
        app,
        default_locale='zh',
        default_translation_directories='locales',
        locale_selector=get_locale
    )
    
    logger.info("Babel已初始化")
    return babel
