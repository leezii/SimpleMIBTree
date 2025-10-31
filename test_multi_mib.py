#!/usr/bin/env python3
"""
测试多MIB文件上传功能的脚本
"""

import requests
import json
import os

def test_single_file_upload():
    """测试单文件上传"""
    print("=== 测试单文件上传 ===")
    
    url = 'http://127.0.0.1:5000/upload-mib'
    
    with open('sample_mibs/SAMPLE-MIB.mib', 'rb') as f:
        files = {'mib_file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 单文件上传成功")
        print(f"   模块: {data.get('module')}")
        print(f"   对象数量: {len(data.get('tree', []))}")
    else:
        print(f"❌ 单文件上传失败: {response.status_code}")

def test_multi_file_upload():
    """测试多文件上传"""
    print("\n=== 测试多文件上传 ===")
    
    url = 'http://127.0.0.1:5000/upload-mib'
    files = []
    
    # 添加多个文件
    file_names = ['SAMPLE-MIB.mib', 'RELATED-MIB.mib', 'CHILD-MIB.mib']
    for file_name in file_names:
        file_path = f'sample_mibs/{file_name}'
        if os.path.exists(file_path):
            files.append(('mib_files', open(file_path, 'rb')))
    
    try:
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 多文件上传成功")
            print(f"   解析的模块数量: {len(data.get('modules', []))}")
            print(f"   总对象数量: {data.get('total_objects', 0)}")
            
            # 显示每个模块的信息
            for module in data.get('modules', []):
                print(f"   - {module['name']}: {module['object_count']} 个对象")
        else:
            print(f"❌ 多文件上传失败: {response.status_code}")
    
    finally:
        # 关闭文件
        for _, file_obj in files:
            file_obj.close()

def test_invalid_files():
    """测试无效文件上传"""
    print("\n=== 测试无效文件上传 ===")
    
    url = 'http://127.0.0.1:5000/upload-mib'
    
    # 创建一个无效文件
    with open('test_invalid.txt', 'w') as f:
        f.write('This is not a MIB file')
    
    with open('test_invalid.txt', 'rb') as f:
        files = {'mib_files': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        if not data.get('success'):
            print(f"✅ 正确拒绝了无效文件: {data.get('error')}")
        else:
            print(f"❌ 意外接受了无效文件")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 清理测试文件
    os.remove('test_invalid.txt')

if __name__ == '__main__':
    print("开始测试多MIB文件上传功能...\n")
    
    # 确保Flask应用正在运行
    try:
        response = requests.get('http://127.0.0.1:5000/mib-parser')
        if response.status_code != 200:
            print("❌ Flask应用未运行，请先启动: python3 app.py")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask应用，请先启动: python3 app.py")
        exit(1)
    
    # 运行测试
    test_single_file_upload()
    test_multi_file_upload()
    test_invalid_files()
    
    print("\n🎉 所有测试完成！")
