#!/usr/bin/env python3
"""
测试 MIB 树形结构解析
"""

import sys
import os
sys.path.append('src')

from mib_parser import mib_parser

def test_sample_mib():
    """测试示例 MIB 文件的树形结构"""
    print("=== 测试 MIB 树形结构解析 ===\n")
    
    # 测试示例 MIB 文件
    sample_file = 'test_data/sample_mibs/SAMPLE-MIB.mib'
    if not os.path.exists(sample_file):
        print(f"❌ 测试文件不存在: {sample_file}")
        return False
    
    try:
        # 解析文件
        result = mib_parser().parse_mib_file(sample_file)
        
        if not result['success']:
            print(f"❌ 解析失败: {result['error']}")
            return False
        
        tree = result['tree']
        print(f"✅ 成功解析文件: {result['module']}")
        print(f"📊 树节点数量: {len(tree)}")
        
        # 打印树形结构
        def print_tree(nodes, indent=0):
            for node in nodes:
                prefix = "  " * indent
                node_type = node.get('type', 'unknown')
                text = node.get('text', 'N/A')
                numeric_oid = node.get('numeric_oid', 'N/A')
                
                print(f"{prefix}📁 {text} [{node_type}]")
                if numeric_oid != 'N/A':
                    print(f"{prefix}   OID: {numeric_oid}")
                
                # 打印详细信息
                if node.get('syntax') and node['syntax'] != 'N/A':
                    print(f"{prefix}   Syntax: {node['syntax']}")
                if node.get('access') and node['access'] != 'N/A':
                    print(f"{prefix}   Access: {node['access']}")
                
                # 递归打印子节点
                if node.get('children'):
                    print_tree(node['children'], indent + 1)
        
        print("\n🌳 树形结构:")
        print_tree(tree)
        
        # 验证层次结构
        def validate_hierarchy(nodes, parent_path=""):
            issues = []
            for node in nodes:
                current_path = f"{parent_path}.{node['text']}" if parent_path else node['text']
                
                # 检查是否有重复的子节点
                children = node.get('children', [])
                child_names = [child['text'] for child in children]
                if len(child_names) != len(set(child_names)):
                    issues.append(f"节点 {current_path} 有重复的子节点")
                
                # 递归检查子节点
                child_issues = validate_hierarchy(children, current_path)
                issues.extend(child_issues)
            
            return issues
        
        issues = validate_hierarchy(tree)
        if issues:
            print(f"\n⚠️  发现的问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n✅ 树形结构验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_files():
    """测试多文件解析"""
    print("\n=== 测试多文件解析 ===\n")
    
    # 测试多个 MIB 文件
    sample_files = [
        'test_data/sample_mibs/SAMPLE-MIB.mib',
        'test_data/sample_mibs/CHILD-MIB.mib',
        'test_data/sample_mibs/RELATED-MIB.mib'
    ]
    
    existing_files = [f for f in sample_files if os.path.exists(f)]
    if not existing_files:
        print("❌ 没有找到测试文件")
        return False
    
    try:
        # 创建 Flask 应用上下文
        from src.app import app
        with app.app_context():
            # 模拟文件对象
            class MockFile:
                def __init__(self, filepath):
                    self.filename = os.path.basename(filepath)
                    self.filepath = filepath
                
                def save(self, path):
                    import shutil
                    shutil.copy2(self.filepath, path)
            
            mock_files = [MockFile(f) for f in existing_files]
            
            # 解析多个文件
            result = mib_parser().parse_multiple_mib_files(mock_files)
        
        if not result['success']:
            print(f"❌ 解析失败: {result['error']}")
            return False
        
        tree = result['tree']
        modules = result.get('modules', [])
        total_objects = result.get('total_objects', 0)
        
        print(f"✅ 成功解析 {len(existing_files)} 个文件")
        print(f"📊 模块数量: {len(modules)}")
        print(f"📊 总对象数量: {total_objects}")
        print(f"📊 树节点数量: {len(tree)}")
        
        # 打印模块信息
        for module in modules:
            print(f"  📦 {module['name']}: {module['object_count']} 个对象")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success1 = test_sample_mib()
    success2 = test_multiple_files()
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！MIB 树形结构解析工作正常")
        sys.exit(0)
    else:
        print(f"\n❌ 部分测试失败")
        sys.exit(1)
