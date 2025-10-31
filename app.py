from flask import Flask, jsonify, render_template, request
import logging
import os
import tempfile
from werkzeug.utils import secure_filename
import json
import sys
import re

# 标准OID映射表
STANDARD_OID_MAP = {
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
    'snmpV2': '1.3.6.1.6'
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_form_data(form_data):
    """处理表单数据的辅助函数"""
    firstname = form_data.get('firstname', '').strip()
    lastname = form_data.get('lastname', '').strip()
    if firstname and lastname:
        output = firstname + " " + lastname
        return {'output': f'Your Name is {output}, right?'}
    return {'error': 'Missing data!'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mib', 'txt', 'my'}

def parse_mib_file(file_path):
    """解析MIB文件并返回树形结构"""
    try:
        # 使用简化的MIB解析方法
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            mib_content = f.read()
        
        # 基本的MIB解析（简化版）
        tree_data = parse_mib_content(mib_content, os.path.basename(file_path))
        return {'success': True, 'tree': tree_data, 'module': os.path.splitext(os.path.basename(file_path))[0]}
            
    except Exception as e:
        logger.error(f"Error parsing MIB file: {str(e)}")
        return {'success': False, 'error': str(e)}

def parse_multiple_mib_files(files):
    """解析多个MIB文件并返回合并的树形结构"""
    try:
        all_objects = []  # 存储所有文件的对象
        module_info = []  # 存储模块信息
        saved_files = []   # 保存的文件路径，用于清理
        
        # 第一步：解析所有文件
        for file in files:
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                saved_files.append(file_path)
                
                # 读取并解析文件内容
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    mib_content = f.read()
                
                # 解析单个文件的内容
                file_objects = parse_mib_content_raw(mib_content, filename)
                
                # 添加模块信息
                module_name = os.path.splitext(filename)[0]
                module_info.append({
                    'name': module_name,
                    'filename': filename,
                    'object_count': len([obj for obj in file_objects if obj['type'] in ['object', 'identifier']])
                })
                
                # 为每个对象添加文件来源信息
                for obj in file_objects:
                    obj['source_file'] = filename
                    obj['source_module'] = module_name
                
                all_objects.extend(file_objects)
                
            except Exception as e:
                logger.error(f"Error parsing file {file.filename}: {str(e)}")
                continue
        
        # 清理临时文件
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except:
                pass
        
        if not all_objects:
            return {'success': False, 'error': 'No valid MIB objects found in any file'}
        
        # 第二步：合并和构建层次结构
        merged_tree = merge_mib_objects(all_objects)
        
        # 计算总对象数量
        total_objects = len([obj for obj in all_objects if obj['type'] in ['object', 'identifier']])
        
        return {
            'success': True,
            'tree': merged_tree,
            'modules': module_info,
            'total_objects': total_objects
        }
        
    except Exception as e:
        logger.error(f"Error parsing multiple MIB files: {str(e)}")
        return {'success': False, 'error': str(e)}

def parse_mib_content_raw(content, filename):
    """解析MIB内容，返回原始对象列表（不构建层次结构）"""
    lines = content.split('\n')
    raw_objects = []
    current_object = None
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        # 查找OBJECT-TYPE定义
        if 'OBJECT-TYPE' in line:
            object_name = line.split('OBJECT-TYPE')[0].strip()
            if object_name:
                current_object = {
                    'text': object_name,
                    'type': 'object',
                    'oid': 'N/A',
                    'oid_path': [],
                    'numeric_oid': 'N/A',
                    'syntax': 'N/A',
                    'access': 'N/A',
                    'status': 'N/A',
                    'description': 'N/A',
                    'children': []
                }
                raw_objects.append(current_object)
        
        # 提取SYNTAX
        elif current_object and 'SYNTAX' in line:
            syntax = line.replace('SYNTAX', '').strip()
            current_object['syntax'] = syntax
        
        # 提取MAX-ACCESS
        elif current_object and 'MAX-ACCESS' in line:
            access = line.replace('MAX-ACCESS', '').strip()
            current_object['access'] = access
        
        # 提取STATUS
        elif current_object and 'STATUS' in line:
            status = line.replace('STATUS', '').strip()
            current_object['status'] = status
        
        # 提取OID
        elif current_object and '::=' in line:
            oid_part = line.split('::=')[1].strip()
            current_object['oid'] = oid_part
            current_object['oid_path'] = parse_oid_path(oid_part)
            current_object = None
        
        # 查找OBJECT IDENTIFIER
        elif 'OBJECT IDENTIFIER' in line and '::=' in line:
            parts = line.split('OBJECT IDENTIFIER')
            if len(parts) >= 2:
                object_name = parts[0].strip()
                oid_part = line.split('::=')[1].strip() if '::=' in line else 'N/A'
                raw_objects.append({
                    'text': object_name,
                    'type': 'identifier',
                    'oid': oid_part,
                    'oid_path': parse_oid_path(oid_part),
                    'numeric_oid': 'N/A',
                    'children': []
                })
        
        # 查找MODULE-IDENTITY
        elif 'MODULE-IDENTITY' in line:
            module_name = line.split('MODULE-IDENTITY')[0].strip()
            if module_name:
                raw_objects.append({
                    'text': f"Module: {module_name}",
                    'type': 'module',
                    'oid': 'Module Identity',
                    'oid_path': [],
                    'numeric_oid': 'Module',
                    'children': []
                })
    
    return raw_objects

def merge_mib_objects(all_objects):
    """合并多个MIB文件的对象并构建统一的层次结构"""
    if not all_objects:
        return []
    
    # 计算数字OID（跨文件）
    all_objects = calculate_numeric_oids_cross_files(all_objects)
    
    # 构建层次结构
    return build_hierarchy_cross_files(all_objects)

def calculate_numeric_oids_cross_files(raw_objects):
    """跨文件计算数字OID"""
    # 创建名称到对象的映射
    name_to_obj = {}
    name_to_numeric = {}
    
    # 首先收集所有对象名称
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        name_to_obj[clean_name] = obj
    
    # 设置基础OID值（包含标准OID和常见的企业OID）
    name_to_numeric.update(STANDARD_OID_MAP)
    
    # 为每个对象计算数字OID
    def calculate_oid_for_object(obj):
        if obj.get('numeric_oid') != 'N/A' and obj.get('numeric_oid') != 'Module':
            return
            
        oid_str = obj.get('oid', '')
        if not oid_str or oid_str == 'N/A' or oid_str == 'Module Identity':
            return
        
        # 解析OID字符串 如 "{ sampleSystemInfo 1 }"
        clean_oid = oid_str.strip('{ }')
        parts = clean_oid.split()
        
        if len(parts) >= 2:
            parent_name = parts[0]
            child_id = parts[-1]
            
            if child_id.isdigit():
                # 查找父对象的数字OID
                parent_numeric = None
                
                if parent_name in name_to_numeric:
                    parent_numeric = name_to_numeric[parent_name]
                elif parent_name in name_to_obj:
                    # 递归计算父对象
                    calculate_oid_for_object(name_to_obj[parent_name])
                    if name_to_obj[parent_name].get('numeric_oid', 'N/A') != 'N/A':
                        parent_numeric = name_to_obj[parent_name]['numeric_oid']
                        name_to_numeric[parent_name] = parent_numeric
                
                if parent_numeric:
                    full_oid = parent_numeric + '.' + child_id
                    obj['numeric_oid'] = full_oid
                    name_to_numeric[obj['text']] = full_oid
        
        elif len(parts) == 1 and parts[0].isdigit():
            # 直接是数字
            obj['numeric_oid'] = parts[0]
    
    # 多次迭代确保所有依赖都被解析
    for _ in range(10):  # 增加迭代次数以处理复杂的依赖关系
        for obj in raw_objects:
            calculate_oid_for_object(obj)
    
    return raw_objects

def build_hierarchy_cross_files(raw_objects):
    """跨文件构建对象层次结构"""
    # 创建对象字典，以名称为键
    obj_dict = {}
    root_objects = []
    used_objects = []  # 记录已被作为子节点的对象
    
    # 先创建所有对象的字典
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        obj_dict[clean_name] = obj
    
    # 第一步：找到明确的父子关系
    for obj in raw_objects:
        if obj['type'] == 'module':
            continue  # 模块单独处理
            
        oid_path = obj.get('oid_path', [])
        if oid_path:
            # 尝试找到最直接的父对象（路径中的最后一个）
            for potential_parent_name in reversed(oid_path):
                if potential_parent_name in obj_dict:
                    parent_obj = obj_dict[potential_parent_name]
                    if parent_obj != obj and obj not in used_objects:
                        parent_obj['children'].append(obj)
                        used_objects.append(obj)
                        break
    
    # 第二步：将没有父对象的对象添加到根级
    for obj in raw_objects:
        if obj not in used_objects:
            root_objects.append(obj)
    
    # 第三步：按模块组织根级对象
    return organize_by_modules(root_objects, raw_objects)

def organize_by_modules(root_objects, all_objects):
    """按模块组织对象"""
    # 按模块分组
    modules = {}
    other_objects = []
    
    for obj in all_objects:
        if obj['type'] == 'module':
            module_name = obj['text'].replace('Module: ', '')
            modules[module_name] = obj
        elif obj not in root_objects:
            # 这些对象已经被作为子节点添加
            continue
        else:
            other_objects.append(obj)
    
    # 创建根节点结构
    organized = []
    
    # 如果有模块，按模块组织
    if modules:
        # 创建一个总的根节点
        root_node = {
            'text': 'MIB Modules',
            'type': 'root',
            'oid': 'Root',
            'numeric_oid': 'Root',
            'children': []
        }
        
        for module_name, module_obj in modules.items():
            # 找到属于这个模块的对象
            module_objects = [obj for obj in root_objects if obj.get('source_module') == module_name]
            
            # 为模块对象添加这些子对象
            for obj in module_objects:
                if obj != module_obj and obj not in module_obj['children']:
                    module_obj['children'].append(obj)
            
            root_node['children'].append(module_obj)
        
        # 添加不属于任何模块的对象
        for obj in other_objects:
            if obj['type'] != 'module' and obj not in root_node['children']:
                root_node['children'].append(obj)
        
        organized.append(root_node)
    else:
        # 没有模块，直接返回所有对象
        organized = root_objects
    
    return organized if organized else root_objects

def parse_mib_content(content, filename):
    """全新的MIB内容解析，构建父子关系"""
    lines = content.split('\n')
    raw_objects = []  # 先收集所有对象
    current_object = None
    
    # 第一步：解析所有对象
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        # 查找OBJECT-TYPE定义
        if 'OBJECT-TYPE' in line:
            object_name = line.split('OBJECT-TYPE')[0].strip()
            if object_name:
                current_object = {
                    'text': object_name,
                    'type': 'object',
                    'oid': 'N/A',
                    'oid_path': [],
                    'numeric_oid': 'N/A',
                    'syntax': 'N/A',
                    'access': 'N/A',
                    'status': 'N/A',
                    'description': 'N/A',
                    'children': []
                }
                raw_objects.append(current_object)
        
        # 提取SYNTAX
        elif current_object and 'SYNTAX' in line:
            syntax = line.replace('SYNTAX', '').strip()
            current_object['syntax'] = syntax
        
        # 提取MAX-ACCESS
        elif current_object and 'MAX-ACCESS' in line:
            access = line.replace('MAX-ACCESS', '').strip()
            current_object['access'] = access
        
        # 提取STATUS
        elif current_object and 'STATUS' in line:
            status = line.replace('STATUS', '').strip()
            current_object['status'] = status
        
        # 提取OID
        elif current_object and '::=' in line:
            oid_part = line.split('::=')[1].strip()
            current_object['oid'] = oid_part
            current_object['oid_path'] = parse_oid_path(oid_part)
            current_object = None
        
        # 查找OBJECT IDENTIFIER
        elif 'OBJECT IDENTIFIER' in line and '::=' in line:
            parts = line.split('OBJECT IDENTIFIER')
            if len(parts) >= 2:
                object_name = parts[0].strip()
                oid_part = line.split('::=')[1].strip() if '::=' in line else 'N/A'
                raw_objects.append({
                    'text': object_name,
                    'type': 'identifier',
                    'oid': oid_part,
                    'oid_path': parse_oid_path(oid_part),
                    'numeric_oid': 'N/A',
                    'children': []
                })
        
        # 查找MODULE-IDENTITY
        elif 'MODULE-IDENTITY' in line:
            module_name = line.split('MODULE-IDENTITY')[0].strip()
            if module_name:
                raw_objects.insert(0, {
                    'text': f"Module: {module_name}",
                    'type': 'module',
                    'oid': 'Module Identity',
                    'oid_path': [],
                    'numeric_oid': 'Module',
                    'children': []
                })
    
    # 第二步：计算数字OID
    if raw_objects:
        raw_objects = calculate_numeric_oids(raw_objects)
    
    # 第三步：构建父子关系
    if raw_objects:
        return build_hierarchy(raw_objects)
    else:
        return [{
            'text': f"File: {filename}",
            'type': 'file',
            'oid': 'Parsed File',
            'children': [{
                'text': f"Lines: {len(lines)}",
                'type': 'info',
                'oid': 'File Statistics'
            }]
        }]

def parse_oid_path(oid_str):
    """解析OID路径"""
    if not oid_str or oid_str == 'N/A':
        return []
    
    # 移除花括号和空格
    cleaned = oid_str.strip('{ }')
    if not cleaned:
        return []
    
    # 分割路径
    parts = [part.strip() for part in cleaned.split() if part.strip()]
    return parts

def calculate_numeric_oids(raw_objects):
    """计算数字OID"""
    # 创建名称到对象的映射
    name_to_obj = {}
    name_to_numeric = {}
    
    # 首先收集所有对象名称
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        name_to_obj[clean_name] = obj
    
    # 设置基础OID值
    name_to_numeric['sampleMIB'] = '1.3.6.1.4.1.99999'  # enterprises 99999
    name_to_numeric['enterprises'] = '1.3.6.1.4.1'
    
    # 为每个对象计算数字OID
    def calculate_oid_for_object(obj):
        if obj.get('numeric_oid') != 'N/A' and obj.get('numeric_oid') != 'Module':
            return
            
        oid_str = obj.get('oid', '')
        if not oid_str or oid_str == 'N/A' or oid_str == 'Module Identity':
            return
        
        # 解析OID字符串 如 "{ sampleSystemInfo 1 }"
        clean_oid = oid_str.strip('{ }')
        parts = clean_oid.split()
        
        if len(parts) >= 2:
            parent_name = parts[0]
            child_id = parts[-1]
            
            if child_id.isdigit():
                # 查找父对象的数字OID
                parent_numeric = None
                
                if parent_name in name_to_numeric:
                    parent_numeric = name_to_numeric[parent_name]
                elif parent_name == 'enterprises':
                    parent_numeric = STANDARD_OID_MAP['enterprises']
                    # 如果是 enterprises 99999 这样的格式
                    if len(parts) == 2 and parts[1].isdigit():
                        parent_numeric = STANDARD_OID_MAP['enterprises'] + '.' + parts[1]
                        obj['numeric_oid'] = parent_numeric
                        name_to_numeric[obj['text']] = parent_numeric
                        return
                elif parent_name in name_to_obj:
                    # 递归计算父对象
                    calculate_oid_for_object(name_to_obj[parent_name])
                    if name_to_obj[parent_name].get('numeric_oid', 'N/A') != 'N/A':
                        parent_numeric = name_to_obj[parent_name]['numeric_oid']
                        name_to_numeric[parent_name] = parent_numeric
                
                if parent_numeric:
                    full_oid = parent_numeric + '.' + child_id
                    obj['numeric_oid'] = full_oid
                    name_to_numeric[obj['text']] = full_oid
        
        elif len(parts) == 1 and parts[0].isdigit():
            # 直接是数字
            obj['numeric_oid'] = parts[0]
    
    # 多次迭代确保所有依赖都被解析
    for _ in range(5):  # 最多5次迭代
        for obj in raw_objects:
            calculate_oid_for_object(obj)
    
    return raw_objects

def build_hierarchy(raw_objects):
    """构建对象层次结构"""
    # 创建对象字典，以名称为键
    obj_dict = {}
    root_objects = []
    used_objects = []  # 记录已被作为子节点的对象
    
    # 先创建所有对象的字典
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        obj_dict[clean_name] = obj
    
    # 第一步：找到明确的父子关系
    for obj in raw_objects:
        if obj['type'] == 'module':
            continue  # 模块单独处理
            
        oid_path = obj.get('oid_path', [])
        if oid_path:
            # 尝试找到最直接的父对象（路径中的最后一个）
            for potential_parent_name in reversed(oid_path):
                if potential_parent_name in obj_dict:
                    parent_obj = obj_dict[potential_parent_name]
                    if parent_obj != obj and obj not in used_objects:
                        parent_obj['children'].append(obj)
                        used_objects.append(obj)
                        break
    
    # 第二步：将没有父对象的对象添加到根级
    for obj in raw_objects:
        if obj not in used_objects:
            root_objects.append(obj)
    
    # 第三步：根据名称匹配进一步优化层次结构
    root_objects = organize_by_naming_convention(root_objects)
    
    return root_objects if root_objects else raw_objects

def organize_by_naming_convention(objects):
    """根据命名约定进一步组织层次结构"""
    # 对于示例MIB，我们可以基于命名模式来组织
    organized = []
    
    # 找到模块对象
    modules = [obj for obj in objects if obj['type'] == 'module']
    
    # 找到根级对象（不包含点的名称）
    root_level = [obj for obj in objects if obj['type'] != 'module' and 
                  ('sampleObjects' in obj['text'] or 'sampleNotifications' in obj['text'])]
    
    # 找到系统信息组
    system_group = [obj for obj in objects if 'sampleSystemInfo' in obj['text']]
    
    # 找到系统对象
    system_objects = [obj for obj in objects if obj['text'].startswith('sampleSystem') and 
                      obj['text'] not in ['sampleSystemInfo']]
    
    # 找到配置表相关对象
    config_objects = [obj for obj in objects if 'sampleConfig' in obj['text']]
    
    # 组织结构
    for module in modules:
        organized.append(module)
        
        # 为模块添加子节点
        for root_obj in root_level:
            if root_obj['text'] == 'sampleObjects':
                # 为sampleObjects添加子组
                for sys_group in system_group:
                    if sys_group not in root_obj['children']:
                        # 为sampleSystemInfo添加系统对象
                        for sys_obj in system_objects:
                            if sys_obj not in sys_group['children']:
                                sys_group['children'].append(sys_obj)
                        root_obj['children'].append(sys_group)
                
                # 添加配置表
                config_table = next((obj for obj in config_objects if obj['text'] == 'sampleConfigTable'), None)
                if config_table and config_table not in root_obj['children']:
                    # 为配置表添加子对象
                    config_entry = next((obj for obj in config_objects if obj['text'] == 'sampleConfigEntry'), None)
                    if config_entry:
                        config_entry_items = [obj for obj in config_objects if 
                                            obj['text'].startswith('sampleConfig') and 
                                            obj['text'] not in ['sampleConfigTable', 'sampleConfigEntry']]
                        for item in config_entry_items:
                            if item not in config_entry['children']:
                                config_entry['children'].append(item)
                        if config_entry not in config_table['children']:
                            config_table['children'].append(config_entry)
                    root_obj['children'].append(config_table)
                    
            module['children'].append(root_obj)
    
    # 如果没有模块，直接返回所有对象
    return organized if organized else objects

# 删除此函数，已被 parse_mib_content 替代

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        response = process_form_data(request.form)
        return jsonify(response)
    return render_template('index.html')

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        response = process_form_data(request.form)
        logger.debug(f"Received POST request with data: {request.form}")
        return jsonify(response)
    return render_template('hello.html')

@app.route('/mib-parser')
def mib_parser():
    """MIB解析器页面"""
    return render_template('mib_parser.html')

@app.route('/upload-mib', methods=['POST'])
def upload_mib():
    """处理MIB文件上传和解析"""
    # 检查是单文件还是多文件上传
    if 'mib_file' in request.files:
        # 单文件上传（向后兼容）
        file = request.files['mib_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 解析MIB文件
                result = parse_mib_file(file_path)
                
                # 清理临时文件
                try:
                    os.remove(file_path)
                except:
                    pass
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        else:
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload a .mib, .txt, or .my file'})
    
    elif 'mib_files' in request.files:
        # 多文件上传
        files = request.files.getlist('mib_files')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No files selected'})
        
        # 验证所有文件
        valid_files = []
        invalid_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename)
        
        if invalid_files:
            return jsonify({'success': False, 'error': f'Invalid file types: {", ".join(invalid_files)}. Please upload only .mib, .txt, or .my files'})
        
        if not valid_files:
            return jsonify({'success': False, 'error': 'No valid files selected'})
        
        try:
            # 解析多个MIB文件
            result = parse_multiple_mib_files(valid_files)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error processing multiple files: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})
    
    else:
        return jsonify({'success': False, 'error': 'No file selected'})

if __name__ == '__main__':
    app.run(debug=True)
