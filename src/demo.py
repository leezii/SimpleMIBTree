#!/usr/bin/env python3
"""
MIB解析器演示脚本
"""
import webbrowser
import time
import os

def main():
    print("🌳 MIB文件解析器演示")
    print("=" * 50)
    
    print("\n✅ 功能特点:")
    print("- 支持拖拽上传MIB文件")
    print("- 树形结构展示MIB对象")
    print("- 解析OBJECT-TYPE、OBJECT IDENTIFIER等")
    print("- 显示语法、访问权限、状态等详细信息")
    print("- 现代化的Web界面")
    
    print("\n📁 项目结构:")
    for root, dirs, files in os.walk('.'):
        # 忽略某些目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.vscode']]
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                print(f"{subindent}{file}")
    
    print("\n🚀 启动说明:")
    print("1. 确保Flask应用正在运行: python app.py")
    print("2. 访问 http://localhost:5000")
    print("3. 点击 '🌳 MIB解析器' 链接")
    print("4. 上传 sample_mibs/SAMPLE-MIB.mib 文件进行测试")
    
    print("\n📊 测试示例文件包含:")
    print("- 模块定义 (MODULE-IDENTITY)")
    print("- 系统信息对象 (sampleSystemName, sampleSystemVersion等)")
    print("- 配置表 (sampleConfigTable)")
    print("- 各种数据类型 (DisplayString, Integer32, 枚举等)")
    
    # 尝试打开浏览器
    try:
        print("\n🌐 正在打开浏览器...")
        webbrowser.open('http://localhost:5000/mib-parser')
    except:
        print("❌ 无法自动打开浏览器，请手动访问 http://localhost:5000/mib-parser")

if __name__ == '__main__':
    main()