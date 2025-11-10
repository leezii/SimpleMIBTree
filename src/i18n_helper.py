"""简单的国际化助手"""
import json
import os

# 翻译数据
TRANSLATIONS = {
    'zh': {
        '网络工具集': '网络工具集',
        '专业的网络管理和开发工具集合': '专业的网络管理和开发工具集合',
        'MIB文件解析器': 'MIB文件解析器',
        '解析和展示MIB文件结构，支持树形显示和OID计算': '解析和展示MIB文件结构，支持树形显示和OID计算',
        'SNMP命令生成器': 'SNMP命令生成器',
        '生成SNMP查询命令，支持v1/v2c/v3协议': '生成SNMP查询命令，支持v1/v2c/v3协议',
        'MIB OID生成器': 'MIB OID生成器',
        '智能OID路径计算和生成，支持批量处理': '智能OID路径计算和生成，支持批量处理',
        '上传MIB文件进行解析': '上传MIB文件进行解析',
        '选择文件或拖拽到此处': '选择文件或拖拽到此处',
        '支持的格式：.mib, .txt, .my': '支持的格式：.mib, .txt, .my',
        '解析': '解析',
        '生成SNMP查询命令': '生成SNMP查询命令',
        '生成MIB OID路径': '生成MIB OID路径',
        '可用工具': '可用工具',
        '选择您需要的工具开始使用': '选择您需要的工具开始使用',
        '开始使用': '开始使用',
        '网络扫描器': '网络扫描器',
        '配置管理器': '配置管理器',
        '即将推出': '即将推出',
        '更多工具开发中': '更多工具开发中',
        '此工具正在开发中，敬请期待！': '此工具正在开发中，敬请期待！',
        '© 2024 网络工具集 - 专业的网络管理解决方案': '© 2024 网络工具集 - 专业的网络管理解决方案'
    },
    'en': {
        '网络工具集': 'Network Tools',
        '专业的网络管理和开发工具集合': 'Professional Network Management and Development Tools',
        'MIB文件解析器': 'MIB File Parser',
        '解析和展示MIB文件结构，支持树形显示和OID计算': 'Parse and display MIB file structure with tree view and OID calculation',
        'SNMP命令生成器': 'SNMP Command Generator',
        '生成SNMP查询命令，支持v1/v2c/v3协议': 'Generate SNMP query commands supporting v1/v2c/v3 protocols',
        'MIB OID生成器': 'MIB OID Generator',
        '智能OID路径计算和生成，支持批量处理': 'Intelligent OID path calculation and generation with batch processing',
        '上传MIB文件进行解析': 'Upload MIB file for parsing',
        '选择文件或拖拽到此处': 'Choose file or drag and drop here',
        '支持的格式：.mib, .txt, .my': 'Supported formats: .mib, .txt, .my',
        '解析': 'Parse',
        '生成SNMP查询命令': 'Generate SNMP Query Commands',
        '生成MIB OID路径': 'Generate MIB OID Paths',
        '可用工具': 'Available Tools',
        '选择您需要的工具开始使用': 'Choose the tool you need to get started',
        '开始使用': 'Get Started',
        '网络扫描器': 'Network Scanner',
        '配置管理器': 'Configuration Manager',
        '即将推出': 'Coming Soon',
        '更多工具开发中': 'More tools in development...',
        '此工具正在开发中，敬请期待！': 'This tool is under development, stay tuned!',
        '© 2024 网络工具集 - 专业的网络管理解决方案': '© 2024 Network Tools - Professional Network Management Solutions'
    }
}

def get_translation(text, lang='zh'):
    """获取翻译文本"""
    return TRANSLATIONS.get(lang, {}).get(text, text)

def get_locale():
    """获取当前语言"""
    # 这里可以从session、cookie或URL参数获取语言
    return 'zh'  # 默认中文
