"""Internationalization support module"""
from flask_babel import Babel
from flask import request, session
import logging

logger = logging.getLogger(__name__)

def get_locale():
    """Get user language preference"""
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
    browser_lang = request.accept_languages.best_match(['en', 'zh']) or 'en'
    logger.info(f"Using browser language: {browser_lang}")
    session['language'] = browser_lang  # Save to session
    session.permanent = True  # Make session persistent
    return browser_lang

def init_babel(app):
    """Initialize Babel internationalization support"""
    # Flask-Babel 3.x uses new way to set locale selector
    # Set through locale_selector parameter of init_app
    babel = Babel()
    
    # Initialize application and set locale selector
    babel.init_app(
        app,
        default_locale='en',
        default_translation_directories='locales',
        locale_selector=get_locale
    )
    
    logger.info("Babel initialized")
    return babel
