#!/usr/bin/env python3
"""
统一的 MIB 文件解析测试框架
整合所有测试功能，提供完整的测试覆盖
"""

import os
import sys
import json
import time
import requests
import traceback
from pathlib import Path
from datetime import datetime

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mib_parser import MIBParser
from flask import Flask

# 创建 Flask 应用和配置
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STANDARD_OID_MAP'] = {
    'iso': '1',
    'org': '1.3',
    'dod': '1.3.6',
    'internet': '1.3.6.1',
    'directory': '1.3.6.1.1',
    'mgmt': '1.3.6.1.2',
    'mib-2': '1.3.6.1.2.1',
    'experimental': '1.3.6.1.3',
    'private': '1.3.6.1.4',
    'enterprises': '1.3.6.1.4.1',
    'security': '1.3.6.1.5',
    'snmpV2': '1.3.6.1.6',
    'interfaces': '1.3.6.1.2.1.2',
    'ip': '1.3.6.1.2.1.4',
    'icmp': '1.3.6.1.2.1.5',
    'tcp': '1.3.6.1.2.1.6',
    'udp': '1.3.6.1.2.1.7',
    'egp': '1.3.6.1.2.1.8',
    'transmission': '1.3.6.1.2.1.10',
    'snmp': '1.3.6.1.2.1.11',
    'at': '1.3.6.1.2.1.3',
    'system': '1.3.6.1.2.1.1'
}

class UnifiedMibTester:
    """统一的 MIB 测试器"""
    
    def __init__(self):
        self.parser = MIBParser()
        self.base_url = 'http://127.0.0.1:5000'
        self.test_results = []
        self.detailed_results = {}
        self.test_data_dir = os.path.join('..', 'test_data')
        
    def log_test(self, test_name, success, details="", data=None):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        
        self.test_results.append(result)
        self.detailed_results[test_name] = result
    
    def check_flask_running(self):
        """检查 Flask 应用是否运行"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_single_file_parsing(self):
        """测试单文件解析功能"""
        print("\n=== 测试单文件解析功能 ===")
        
        # 测试示例 MIB 文件
        sample_file = os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib')
        if os.path.exists(sample_file):
            try:
                with app.app_context():
                    result = self.parser.parse_mib_file(sample_file)
                
                if result['success']:
                    tree = result['tree']
                    object_count = self.count_objects(tree)
                    
                    # 验证关键对象
                    key_objects = ['sampleSystemName', 'sampleSystemVersion', 'sampleConfigTable']
                    found_objects = self.find_objects_by_name(tree, key_objects)
                    valid_oids = self.find_valid_oids(tree, '1.3.6.1.4.1.99999')
                    
                    data = {
                        'module': result['module'],
                        'object_count': object_count,
                        'key_objects': found_objects,
                        'valid_oids_count': len(valid_oids),
                        'sample_oids': valid_oids[:3],
                        'tree_structure_valid': len(tree) > 0
                    }
                    
                    self.log_test("单文件解析 - 示例MIB", True, 
                                f"模块: {result['module']}, 对象数: {object_count}", data)
                else:
                    self.log_test("单文件解析 - 示例MIB", False, result.get('error', ''))
            except Exception as e:
                self.log_test("单文件解析 - 示例MIB", False, f"异常: {str(e)}")
        else:
            self.log_test("单文件解析 - 示例MIB", False, "文件不存在")
    
    def test_multiple_file_parsing(self):
        """测试多文件解析功能"""
        print("\n=== 测试多文件解析功能 ===")
        
        sample_files = [
            os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib'),
            os.path.join(self.test_data_dir, 'sample_mibs', 'RELATED-MIB.mib'),
            os.path.join(self.test_data_dir, 'sample_mibs', 'CHILD-MIB.mib')
        ]
        
        existing_files = [f for f in sample_files if os.path.exists(f)]
        if len(existing_files) >= 2:
            try:
                # 创建模拟文件对象
                class MockFile:
                    def __init__(self, filename, content):
                        self.filename = filename
                        self._content = content
                    
                    def save(self, path):
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(self._content)
                
                mock_files = []
                for file_path in existing_files:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    mock_files.append(MockFile(os.path.basename(file_path), content))
                
                with app.app_context():
                    result = self.parser.parse_multiple_mib_files(mock_files)
                
                if result['success']:
                    modules_info = result.get('modules', [])
                    tree = result['tree']
                    imported_objects = self.find_objects_with_syntax(tree, 'SampleStatus')
                    
                    data = {
                        'modules_count': len(modules_info),
                        'total_objects': result.get('total_objects', 0),
                        'modules': modules_info,
                        'cross_file_refs': len(imported_objects),
                        'imported_objects': imported_objects,
                        'tree_structure_valid': len(tree) > 0
                    }
                    
                    self.log_test("多文件解析 - 示例MIBs", True,
                                f"模块数: {len(modules_info)}, 总对象数: {result.get('total_objects', 0)}", data)
                else:
                    self.log_test("多文件解析 - 示例MIBs", False, result.get('error', ''))
            except Exception as e:
                self.log_test("多文件解析 - 示例MIBs", False, f"异常: {str(e)}")
        else:
            self.log_test("多文件解析 - 示例MIBs", False, "文件数量不足")
    
    def test_mib2_standard_files(self):
        """测试 MIB-II 标准文件"""
        print("\n=== 测试 MIB-II 标准文件 ===")
        
        mib2_files = [
            os.path.join(self.test_data_dir, 'mib2_files', 'IF-MIB.txt'),
            os.path.join(self.test_data_dir, 'mib2_files', 'IP-MIB.txt'),
            os.path.join(self.test_data_dir, 'mib2_files', 'TCP-MIB.txt'),
            os.path.join(self.test_data_dir, 'mib2_files', 'UDP-MIB.txt')
        ]
        
        existing_files = [f for f in mib2_files if os.path.exists(f)]
        if existing_files:
            try:
                class MockFile:
                    def __init__(self, filename, content):
                        self.filename = filename
                        self._content = content
                    
                    def save(self, path):
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(self._content)
                
                mock_files = []
                for file_path in existing_files:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    mock_files.append(MockFile(os.path.basename(file_path), content))
                
                with app.app_context():
                    result = self.parser.parse_multiple_mib_files(mock_files)
                
                if result['success']:
                    modules_info = result.get('modules', [])
                    tree = result['tree']
                    groups = self.find_mib2_groups(tree)
                    mib2_oids = self.find_valid_oids(tree, '1.3.6.1.2.1')
                    
                    data = {
                        'modules_count': len(modules_info),
                        'total_objects': result.get('total_objects', 0),
                        'modules': modules_info,
                        'mib2_groups': list(groups.keys()),
                        'mib2_oids_count': len(mib2_oids),
                        'is_mib2_tree': tree and len(tree) > 0 and tree[0].get('text') == 'MIB-II Tree'
                    }
                    
                    self.log_test("MIB-II 标准文件解析", True,
                                f"模块数: {len(modules_info)}, 总对象数: {result.get('total_objects', 0)}", data)
                    
                    # 验证 MIB-II 层次结构
                    if tree and len(tree) > 0:
                        root = tree[0]
                        if root.get('text') == 'MIB-II Tree':
                            self.log_test("MIB-II 层次结构构建", True, "正确识别 MIB-II 树结构")
                        else:
                            self.log_test("MIB-II 层次结构构建", False, f"根节点: {root.get('text', 'N/A')}")
                else:
                    self.log_test("MIB-II 标准文件解析", False, result.get('error', ''))
            except Exception as e:
                self.log_test("MIB-II 标准文件解析", False, f"异常: {str(e)}")
        else:
            self.log_test("MIB-II 标准文件解析", False, "MIB-II 文件不存在")
    
    def test_web_api_single_file(self):
        """测试 Web API - 单文件上传"""
        print("\n=== 测试 Web API - 单文件上传 ===")
        
        if not self.check_flask_running():
            self.log_test("Web API 单文件上传", False, "Flask 应用未运行")
            return
        
        sample_file = os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib')
        if os.path.exists(sample_file):
            try:
                with open(sample_file, 'rb') as f:
                    files = {'mib_file': f}
                    response = requests.post(f"{self.base_url}/upload-mib", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log_test("Web API 单文件上传", True,
                                    f"模块: {data.get('module')}, 对象数: {len(data.get('tree', []))}")
                    else:
                        self.log_test("Web API 单文件上传", False, data.get('error', ''))
                else:
                    self.log_test("Web API 单文件上传", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test("Web API 单文件上传", False, f"异常: {str(e)}")
        else:
            self.log_test("Web API 单文件上传", False, "测试文件不存在")
    
    def test_web_api_multi_file(self):
        """测试 Web API - 多文件上传"""
        print("\n=== 测试 Web API - 多文件上传 ===")
        
        if not self.check_flask_running():
            self.log_test("Web API 多文件上传", False, "Flask 应用未运行")
            return
        
        file_paths = [
            os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib'),
            os.path.join(self.test_data_dir, 'sample_mibs', 'RELATED-MIB.mib')
        ]
        
        existing_files = [(os.path.basename(path), open(path, 'rb')) 
                        for path in file_paths if os.path.exists(path)]
        
        if len(existing_files) >= 2:
            try:
                files = [('mib_files', file_obj) for (name, file_obj) in existing_files]
                response = requests.post(f"{self.base_url}/upload-mib", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log_test("Web API 多文件上传", True,
                                    f"模块数: {len(data.get('modules', []))}, 总对象数: {data.get('total_objects', 0)}")
                    else:
                        self.log_test("Web API 多文件上传", False, data.get('error', ''))
                else:
                    self.log_test("Web API 多文件上传", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test("Web API 多文件上传", False, f"异常: {str(e)}")
            finally:
                # 关闭文件
                for _, file_obj in existing_files:
                    file_obj.close()
        else:
            self.log_test("Web API 多文件上传", False, "文件数量不足")
    
    def test_web_api_zip_file(self):
        """测试 Web API - ZIP 文件上传"""
        print("\n=== 测试 Web API - ZIP 文件上传 ===")
        
        if not self.check_flask_running():
            self.log_test("Web API ZIP 文件上传", False, "Flask 应用未运行")
            return
        
        zip_files = [
            os.path.join(self.test_data_dir, 'MIB.zip'),
            os.path.join(self.test_data_dir, 'test_mibs.zip'),
            os.path.join(self.test_data_dir, 'mib2_files.zip')
        ]
        
        for zip_file in zip_files:
            if os.path.exists(zip_file):
                try:
                    with open(zip_file, 'rb') as f:
                        files = {'mib_file': f}
                        response = requests.post(f"{self.base_url}/upload-mib", files=files, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            zip_info = data.get('zip_info', {})
                            self.log_test(f"Web API ZIP 上传 - {os.path.basename(zip_file)}", True,
                                        f"提取文件数: {zip_info.get('extracted_files', 0)}, 总对象数: {data.get('total_objects', 0)}")
                        else:
                            self.log_test(f"Web API ZIP 上传 - {os.path.basename(zip_file)}", False, 
                                        data.get('error', ''))
                    else:
                        self.log_test(f"Web API ZIP 上传 - {os.path.basename(zip_file)}", False, 
                                    f"HTTP {response.status_code}")
                except Exception as e:
                    self.log_test(f"Web API ZIP 上传 - {os.path.basename(zip_file)}", False, f"异常: {str(e)}")
            else:
                self.log_test(f"Web API ZIP 上传 - {os.path.basename(zip_file)}", False, "文件不存在")
    
    def test_cross_file_dependencies(self):
        """测试跨文件依赖关系"""
        print("\n=== 测试跨文件依赖关系 ===")
        
        related_file = os.path.join(self.test_data_dir, 'sample_mibs', 'RELATED-MIB.mib')
        if os.path.exists(related_file):
            try:
                with app.app_context():
                    result = self.parser.parse_mib_file(related_file)
                
                if result['success']:
                    tree = result['tree']
                    has_imported_objects = False
                    
                    def check_imported_objects(nodes):
                        nonlocal has_imported_objects
                        for node in nodes:
                            if 'SampleStatus' in str(node.get('syntax', '')):
                                has_imported_objects = True
                            if node.get('children'):
                                check_imported_objects(node['children'])
                    
                    check_imported_objects(tree)
                    
                    if has_imported_objects:
                        self.log_test("跨文件依赖关系检测", True, "检测到导入的 SampleStatus")
                    else:
                        self.log_test("跨文件依赖关系检测", False, "未检测到导入的对象")
                else:
                    self.log_test("跨文件依赖关系检测", False, result.get('error', ''))
            except Exception as e:
                self.log_test("跨文件依赖关系检测", False, f"异常: {str(e)}")
        else:
            self.log_test("跨文件依赖关系检测", False, "RELATED-MIB 文件不存在")
    
    def test_oid_calculation_accuracy(self):
        """测试 OID 计算准确性"""
        print("\n=== 测试 OID 计算准确性 ===")
        
        sample_file = os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib')
        if os.path.exists(sample_file):
            try:
                with app.app_context():
                    result = self.parser.parse_mib_file(sample_file)
                
                if result['success']:
                    tree = result['tree']
                    found_valid_oid = False
                    
                    def check_oids(nodes):
                        nonlocal found_valid_oid
                        for node in nodes:
                            numeric_oid = node.get('numeric_oid', '')
                            if numeric_oid and numeric_oid != 'N/A' and numeric_oid.startswith('1.3.6.1.4.1.99999'):
                                found_valid_oid = True
                            if node.get('children'):
                                check_oids(node['children'])
                    
                    check_oids(tree)
                    
                    if found_valid_oid:
                        self.log_test("OID 计算准确性", True, "发现正确的企业 OID")
                    else:
                        self.log_test("OID 计算准确性", False, "未发现预期的企业 OID")
                else:
                    self.log_test("OID 计算准确性", False, result.get('error', ''))
            except Exception as e:
                self.log_test("OID 计算准确性", False, f"异常: {str(e)}")
        else:
            self.log_test("OID 计算准确性", False, "测试文件不存在")
    
    def test_performance_analysis(self):
        """性能分析测试"""
        print("\n=== 性能分析测试 ===")
        
        # 测试单文件解析性能
        sample_file = os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib')
        if os.path.exists(sample_file):
            try:
                start_time = time.time()
                with app.app_context():
                    result = self.parser.parse_mib_file(sample_file)
                single_file_time = time.time() - start_time
                
                if result['success']:
                    object_count = self.count_objects(result['tree'])
                    objects_per_second = object_count / single_file_time if single_file_time > 0 else 0
                    
                    data = {
                        'single_file_time': single_file_time,
                        'object_count': object_count,
                        'objects_per_second': objects_per_second
                    }
                    
                    self.log_test("单文件解析性能", True, 
                                f"时间: {single_file_time:.3f}s, 对象数: {object_count}, 速率: {objects_per_second:.1f} obj/s", data)
                else:
                    self.log_test("单文件解析性能", False, result.get('error', ''))
            except Exception as e:
                self.log_test("单文件解析性能", False, f"异常: {str(e)}")
        
        # 测试多文件解析性能
        mib2_files = [
            os.path.join(self.test_data_dir, 'mib2_files', 'IF-MIB.txt'),
            os.path.join(self.test_data_dir, 'mib2_files', 'IP-MIB.txt')
        ]
        
        existing_files = [f for f in mib2_files if os.path.exists(f)]
        if len(existing_files) >= 2:
            try:
                class MockFile:
                    def __init__(self, filename, content):
                        self.filename = filename
                        self._content = content
                    
                    def save(self, path):
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(self._content)
                
                mock_files = []
                for file_path in existing_files:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    mock_files.append(MockFile(os.path.basename(file_path), content))
                
                start_time = time.time()
                with app.app_context():
                    result = self.parser.parse_multiple_mib_files(mock_files)
                multi_file_time = time.time() - start_time
                
                if result['success']:
                    total_objects = result.get('total_objects', 0)
                    objects_per_second = total_objects / multi_file_time if multi_file_time > 0 else 0
                    
                    data = {
                        'multi_file_time': multi_file_time,
                        'total_objects': total_objects,
                        'objects_per_second': objects_per_second,
                        'files_processed': len(existing_files)
                    }
                    
                    self.log_test("多文件解析性能", True, 
                                f"时间: {multi_file_time:.3f}s, 对象数: {total_objects}, 速率: {objects_per_second:.1f} obj/s", data)
                else:
                    self.log_test("多文件解析性能", False, result.get('error', ''))
            except Exception as e:
                self.log_test("多文件解析性能", False, f"异常: {str(e)}")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        try:
            # 测试不存在的文件
            with app.app_context():
                result = self.parser.parse_mib_file('nonexistent.mib')
            if not result['success']:
                self.log_test("不存在文件错误处理", True, "正确返回错误")
            else:
                self.log_test("不存在文件错误处理", False, "应该返回错误")
            
            # 测试空文件
            empty_file = '../test_empty.mib'
            with open(empty_file, 'w') as f:
                f.write('')
            
            with app.app_context():
                result = self.parser.parse_mib_file(empty_file)
            os.remove(empty_file)
            
            if result['success']:
                self.log_test("空文件处理", True, "正确处理空文件")
            else:
                self.log_test("空文件处理", False, result.get('error', ''))
                
        except Exception as e:
            self.log_test("错误处理测试", False, f"异常: {str(e)}")
    
    def test_tree_structure_validation(self):
        """测试树形结构验证"""
        print("\n=== 测试树形结构验证 ===")
        
        sample_file = os.path.join(self.test_data_dir, 'sample_mibs', 'SAMPLE-MIB.mib')
        if os.path.exists(sample_file):
            try:
                with app.app_context():
                    result = self.parser.parse_mib_file(sample_file)
                
                if result['success']:
                    tree = result['tree']
                    
                    # 验证树形结构
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
                    
                    data = {
                        'tree_depth': self.calculate_tree_depth(tree),
                        'total_nodes': len(self.flatten_tree(tree)),
                        'structure_issues': issues
                    }
                    
                    if issues:
                        self.log_test("树形结构验证", False, f"发现 {len(issues)} 个结构问题", data)
                    else:
                        self.log_test("树形结构验证", True, f"树形结构正确，深度: {data['tree_depth']}", data)
                else:
                    self.log_test("树形结构验证", False, result.get('error', ''))
            except Exception as e:
                self.log_test("树形结构验证", False, f"异常: {str(e)}")
        else:
            self.log_test("树形结构验证", False, "测试文件不存在")
    
    # 辅助方法
    def count_objects(self, nodes):
        """递归计算对象数量"""
        count = 0
        for node in nodes:
            if node['type'] in ['object', 'identifier']:
                count += 1
            if node.get('children'):
                count += self.count_objects(node['children'])
        return count
    
    def find_objects_by_name(self, nodes, names):
        """根据名称查找对象"""
        found = []
        for node in nodes:
            if node['text'] in names:
                found.append(node['text'])
            if node.get('children'):
                found.extend(self.find_objects_by_name(node['children'], names))
        return found
    
    def find_objects_with_syntax(self, nodes, syntax_name):
        """查找使用特定语法的对象"""
        found = []
        for node in nodes:
            if syntax_name in str(node.get('syntax', '')):
                found.append(node['text'])
            if node.get('children'):
                found.extend(self.find_objects_with_syntax(node['children'], syntax_name))
        return found
    
    def find_valid_oids(self, nodes, oid_prefix):
        """查找有效的 OID"""
        valid_oids = []
        for node in nodes:
            numeric_oid = node.get('numeric_oid', '')
            if numeric_oid and numeric_oid != 'N/A' and numeric_oid.startswith(oid_prefix):
                valid_oids.append((node['text'], numeric_oid))
            if node.get('children'):
                valid_oids.extend(self.find_valid_oids(node['children'], oid_prefix))
        return valid_oids
    
    def find_mib2_groups(self, nodes):
        """查找 MIB-II 组"""
        groups = {}
        for node in nodes:
            if node.get('type') == 'group':
                groups[node['text']] = node
            if node.get('children'):
                child_groups = self.find_mib2_groups(node['children'])
                groups.update(child_groups)
        return groups
    
    def calculate_tree_depth(self, nodes):
        """计算树的深度"""
        if not nodes:
            return 0
        max_depth = 0
        for node in nodes:
            children = node.get('children', [])
            if children:
                depth = 1 + self.calculate_tree_depth(children)
                max_depth = max(max_depth, depth)
        return max_depth
    
    def flatten_tree(self, nodes):
        """将树展平为节点列表"""
        flat = []
        for node in nodes:
            flat.append(node)
            if node.get('children'):
                flat.extend(self.flatten_tree(node['children']))
        return flat
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始统一的 MIB 文件解析测试")
        print("=" * 70)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python 版本: {sys.version.split()[0]}")
        print("=" * 70)
        
        # 核心功能测试
        self.test_single_file_parsing()
        self.test_multiple_file_parsing()
        self.test_mib2_standard_files()
        
        # Web API 测试
        self.test_web_api_single_file()
        self.test_web_api_multi_file()
        self.test_web_api_zip_file()
        
        # 功能验证测试
        self.test_cross_file_dependencies()
        self.test_oid_calculation_accuracy()
        self.test_tree_structure_validation()
        
        # 性能测试
        self.test_performance_analysis()
        
        # 错误处理测试
        self.test_error_handling()
        
        # 总结
        self.print_summary()
        self.save_detailed_report()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 70)
        print("📊 测试总结")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 70)
    
    def save_detailed_report(self):
        """保存详细报告"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'test_environment': {
                    'python_version': sys.version,
                    'framework': 'Unified MIB Test Suite',
                    'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'working_directory': os.getcwd()
                },
                'summary': {
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r['success']),
                    'failed_tests': sum(1 for r in self.test_results if not r['success']),
                    'success_rate': (sum(1 for r in self.test_results if r['success']) / len(self.test_results) * 100)
                },
                'detailed_results': self.detailed_results
            }
            
            # 保存到 tests 目录
            report_path = os.path.join(os.path.dirname(__file__), 'mib_unified_test_report.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📄 详细报告已保存到: {report_path}")
        except Exception as e:
            print(f"⚠️ 保存报告失败: {e}")

if __name__ == '__main__':
    tester = UnifiedMibTester()
    tester.run_all_tests()
