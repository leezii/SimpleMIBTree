#!/usr/bin/env python3
import requests
import os

def test_mib_parser():
    """测试MIB解析器功能"""
    url = 'http://localhost:5000/upload-mib'
    
    # 检查示例MIB文件是否存在
    mib_file_path = 'sample_mibs/SAMPLE-MIB.mib'
    if not os.path.exists(mib_file_path):
        print(f"错误: 找不到测试文件 {mib_file_path}")
        return
    
    # 准备文件上传
    with open(mib_file_path, 'rb') as f:
        files = {'mib_file': f}
        
        try:
            response = requests.post(url, files=files)
            result = response.json()
            
            print("=== MIB解析器测试结果 ===")
            print(f"状态: {'成功' if result.get('success') else '失败'}")
            
            if result.get('success'):
                print(f"模块名: {result.get('module', 'N/A')}")
                print(f"解析的根对象数量: {len(result.get('tree', []))}")
                print("\n=== 层次结构 ===")
                def print_tree(objects, indent=0):
                    for i, obj in enumerate(objects):
                        prefix = '  ' * indent + f"{i+1}. "
                        print(f"{prefix}{obj.get('text', 'Unknown')} ({obj.get('type', 'unknown')})")
                        print(f"{' ' * len(prefix)}OID: {obj.get('oid', 'N/A')}")
                        # 显示数字OID
                        if obj.get('numeric_oid') and obj.get('numeric_oid') not in ['N/A', 'Module']:
                            print(f"{' ' * len(prefix)}🔢 数字OID: {obj.get('numeric_oid')}")
                        if obj.get('syntax') and obj.get('syntax') != 'N/A':
                            print(f"{' ' * len(prefix)}语法: {obj.get('syntax')}")
                        if obj.get('access') and obj.get('access') != 'N/A':
                            print(f"{' ' * len(prefix)}访问: {obj.get('access')}")
                        if obj.get('status') and obj.get('status') != 'N/A':
                            print(f"{' ' * len(prefix)}状态: {obj.get('status')}")
                        print()
                        
                        # 递归打印子节点
                        if obj.get('children'):
                            print_tree(obj['children'], indent + 1)
                
                print_tree(result.get('tree', []))
            else:
                print(f"错误: {result.get('error', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            print("错误: 无法连接到Flask服务器。请确保服务器正在运行 (python app.py)")
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == '__main__':
    test_mib_parser()