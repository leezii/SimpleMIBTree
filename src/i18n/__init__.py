"""国际化支持模块"""
from flask_babelex import Babel
from flask import request

def get_locale():
    """获取用户语言偏好"""
    # 1. 检查URL参数中的语言设置
    lang = request.args.get('lang')
    if lang in ['zh', 'en']:
        return lang
    
    # 2. 检查session中的语言设置
    if hasattr(request, 'session') and 'language' in request.session:
        return request.session['language']
    
    # 3. 检查浏览器语言设置
    return request.accept_languages.best_match(['zh', 'en']) or 'zh'

def init_babel(app):
    """初始化Babel国际化支持"""
    babel = Babel(app)
    babel.init_app(app, locale_selector=get_locale)
    return babel
