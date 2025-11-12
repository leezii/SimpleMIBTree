#!/usr/bin/env python3
"""
MIB.zip 解析缺陷修复验证脚本
"""

import sys
import os
sys.path.append('src')

from mib_parser import mib_parser
from file_handler import extract_zip_file
import io

def test_mib_zip_fix():
    """测试 MIB.zip 解析修复"""
    print("=== MIB.zip 解析缺陷修复验证 ===\n")
    
    # 读取 MIB.zip 文件
    zip_path = 'test_data/MIB.zip'
    if not os.path.exists(zip_path):
        print(f"❌ 测试文件不存在: {zip_path}")
        return False
    
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    # 模拟 ZIP 文件对象
    class MockZipFile:
        def __init__(self, filename, content):
            self.filename = filename
            self.content = content
        
        def read(self):
            return self.content
    
    try:
        # 提取文件
        mock_zip = MockZipFile('MIB.zip', zip_content)
        extracted_files = extract_zip_file(mock_zip)
        
        # 过滤掉 macOS 系统文件
        mib_files = [f for f in extracted_files if not f.filename.startswith('__MACOSX')]
        
        print(f"✅ 成功提取 {len(mib_files)} 个有效 MIB 文件")
        
        # 解析所有文件
        parser = mib_parser()
        all_objects = []
        
        for file_obj in mib_files:
            file_objects = parser.parse_mib_content_raw(file_obj.content, file_obj.filename)
            all_objects.extend(file_objects)
        
        # 统计结果
        total_objects = len([obj for obj in all_objects if obj['type'] in ['object', 'identifier']])
        modules = len([obj for obj in all_objects if obj['type'] == 'module'])
        
        print(f"\n📊 解析统计:")
        print(f"  - 总对象数: {total_objects}")
        print(f"  - 模块数: {modules}")
        print(f"  - 解析成功: {total_objects > 0}")
        
        # 验证修复效果
        if total_objects > 1000:  # 期望解析出大量对象
            print(f"\n🎉 MIB.zip 解析缺陷修复成功！")
            print(f"   修复前: 只能解析 1 个模块对象")
            print(f"   修复后: 成功解析 {total_objects} 个 MIB 对象")
            print(f"   性能提升: {total_objects} 倍")
            return True
        else:
            print(f"\n⚠️  解析结果不理想，可能需要进一步调试")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_mib_zip_fix()
    sys.exit(0 if success else 1)
