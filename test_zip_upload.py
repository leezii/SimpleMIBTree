#!/usr/bin/env python3
"""
测试ZIP文件上传功能
"""

import requests
import zipfile
import io
import os

def test_zip_upload():
    """测试ZIP文件上传功能"""
    
    # 创建测试ZIP文件
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加现有的MIB文件到ZIP
        mib_files = [
            'sample_mibs/CHILD-MIB.mib',
            'sample_mibs/RELATED-MIB.mib',
            'sample_mibs/SAMPLE-MIB.mib'
        ]
        
        for mib_file in mib_files:
            if os.path.exists(mib_file):
                zip_file.write(mib_file, os.path.basename(mib_file))
                print(f"Added {mib_file} to ZIP")
    
    zip_buffer.seek(0)
    
    # 发送到Flask应用
    url = 'http://127.0.0.1:5000/upload-mib'
    
    files = {'mib_files': ('test_mibs.zip', zip_buffer, 'application/zip')}
    
    try:
        print("正在上传ZIP文件到服务器...")
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("上传成功！")
            print(f"解析结果: {result}")
            
            if result.get('success'):
                print(f"✅ 成功解析 {result.get('total_objects', 0)} 个对象")
                if result.get('zip_info'):
                    for zip_info in result['zip_info']:
                        print(f"📦 ZIP文件 {zip_info['filename']}: 提取了 {zip_info['extracted_files']} 个MIB文件")
                if result.get('modules'):
                    print("📋 解析的模块:")
                    for module in result['modules']:
                        print(f"  - {module['name']}: {module['object_count']} 个对象")
            else:
                print(f"❌ 解析失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务器，请确保服务器正在运行在 http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_zip_upload()
