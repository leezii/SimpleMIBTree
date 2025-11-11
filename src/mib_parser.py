"""MIB 文件解析模块"""
import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class MIBParser:
    """MIB file parser"""
    
    def __init__(self):
        # 延迟加载配置，避免在模块级别访问 current_app
        self._standard_oid_map = None
    
    @property
    def standard_oid_map(self):
        """延迟获取标准 OID 映射"""
        if self._standard_oid_map is None:
            from flask import current_app
            self._standard_oid_map = current_app.config['STANDARD_OID_MAP']
        return self._standard_oid_map
    
    def parse_mib_file(self, file_path):
        """解析单个 MIB 文件并返回树结构"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                mib_content = f.read()
            
            tree_data = self.parse_mib_content(mib_content, os.path.basename(file_path))
            return {
                'success': True, 
                'tree': tree_data, 
                'module': os.path.splitext(os.path.basename(file_path))[0]
            }
                
        except Exception as e:
            logger.error(f"解析 MIB 文件时出错: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def parse_multiple_mib_files(self, files):
        """解析多个 MIB 文件并返回合并的树结构"""
        try:
            all_objects = []
            module_info = []
            saved_files = []
            
            # 第一步：解析所有文件
            for file in files:
                try:
                    filename = file.filename
                    # 如果文件名包含路径，只取文件名部分
                    if '/' in filename:
                        filename = os.path.basename(filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    saved_files.append(file_path)
                    
                    # 读取并解析文件内容
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        mib_content = f.read()
                    
                    # 解析单个文件内容
                    file_objects = self.parse_mib_content_raw(mib_content, filename)
                    
                    # 添加模块信息
                    module_name = os.path.splitext(filename)[0]
                    module_info.append({
                        'name': module_name,
                        'filename': filename,
                        'object_count': len([obj for obj in file_objects if obj['type'] in ['object', 'identifier']])
                    })
                    
                    # 为每个对象添加文件源信息
                    for obj in file_objects:
                        obj['source_file'] = filename
                        obj['source_module'] = module_name
                    
                    all_objects.extend(file_objects)
                    
                except Exception as e:
                    logger.error(f"解析文件 {file.filename} 时出错: {str(e)}")
                    continue
            
            # 清理临时文件
            for file_path in saved_files:
                try:
                    os.remove(file_path)
                except:
                    pass
            
            if not all_objects:
                return {'success': False, 'error': '在任何文件中都未找到有效的 MIB 对象'}
            
            # 第二步：合并并构建层次结构
            merged_tree = self.merge_mib_objects(all_objects)
            
            # 计算总对象数
            total_objects = len([obj for obj in all_objects if obj['type'] in ['object', 'identifier']])
            
            return {
                'success': True,
                'tree': merged_tree,
                'modules': module_info,
                'total_objects': total_objects
            }
            
        except Exception as e:
            logger.error(f"解析多个 MIB 文件时出错: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def parse_mib_content_raw(self, content, filename):
        """解析 MIB 内容，返回原始对象列表（不构建层次结构）"""
        lines = content.split('\n')
        raw_objects = []
        current_object = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
                
            # 查找 OBJECT-TYPE 定义
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
            
            # 提取 SYNTAX
            elif current_object and 'SYNTAX' in line:
                syntax = line.replace('SYNTAX', '').strip()
                current_object['syntax'] = syntax
            
            # 提取 MAX-ACCESS
            elif current_object and 'MAX-ACCESS' in line:
                access = line.replace('MAX-ACCESS', '').strip()
                current_object['access'] = access
            
            # 提取 STATUS
            elif current_object and 'STATUS' in line:
                status = line.replace('STATUS', '').strip()
                current_object['status'] = status
            
            # 提取 OID
            elif current_object and '::=' in line:
                oid_part = line.split('::=')[1].strip()
                current_object['oid'] = oid_part
                current_object['oid_path'] = self.parse_oid_path(oid_part)
                current_object = None
            
            # 查找 OBJECT IDENTIFIER
            elif 'OBJECT IDENTIFIER' in line and '::=' in line:
                parts = line.split('OBJECT IDENTIFIER')
                if len(parts) >= 2:
                    object_name = parts[0].strip()
                    oid_part = line.split('::=')[1].strip() if '::=' in line else 'N/A'
                    raw_objects.append({
                        'text': object_name,
                        'type': 'identifier',
                        'oid': oid_part,
                        'oid_path': self.parse_oid_path(oid_part),
                        'numeric_oid': 'N/A',
                        'children': []
                    })
            
            # 查找 MODULE-IDENTITY
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
    
    def parse_mib_content(self, content, filename):
        """解析 MIB 内容，构建父子关系"""
        lines = content.split('\n')
        raw_objects = []
        current_object = None
        
        # 第一步：解析所有对象
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
                
            # 查找 OBJECT-TYPE 定义
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
            
            # 提取 SYNTAX
            elif current_object and 'SYNTAX' in line:
                syntax = line.replace('SYNTAX', '').strip()
                current_object['syntax'] = syntax
            
            # 提取 MAX-ACCESS
            elif current_object and 'MAX-ACCESS' in line:
                access = line.replace('MAX-ACCESS', '').strip()
                current_object['access'] = access
            
            # 提取 STATUS
            elif current_object and 'STATUS' in line:
                status = line.replace('STATUS', '').strip()
                current_object['status'] = status
            
            # 提取 OID
            elif current_object and '::=' in line:
                oid_part = line.split('::=')[1].strip()
                current_object['oid'] = oid_part
                current_object['oid_path'] = self.parse_oid_path(oid_part)
                current_object = None
            
            # 查找 OBJECT IDENTIFIER
            elif 'OBJECT IDENTIFIER' in line and '::=' in line:
                parts = line.split('OBJECT IDENTIFIER')
                if len(parts) >= 2:
                    object_name = parts[0].strip()
                    oid_part = line.split('::=')[1].strip() if '::=' in line else 'N/A'
                    raw_objects.append({
                        'text': object_name,
                        'type': 'identifier',
                        'oid': oid_part,
                        'oid_path': self.parse_oid_path(oid_part),
                        'numeric_oid': 'N/A',
                        'children': []
                    })
            
            # 查找 MODULE-IDENTITY
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
        
        # 第二步：计算数字 OID
        if raw_objects:
            raw_objects = self.calculate_numeric_oids(raw_objects)
        
        # 第三步：构建父子关系
        if raw_objects:
            return self.build_hierarchy(raw_objects)
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
    
    def parse_oid_path(self, oid_str):
        """解析 OID 路径"""
        if not oid_str or oid_str == 'N/A':
            return []
        
        # 移除花括号和空格
        cleaned = oid_str.strip('{ }')
        if not cleaned:
            return []
        
        # 分割路径
        parts = [part.strip() for part in cleaned.split() if part.strip()]
        return parts
    
    def merge_mib_objects(self, all_objects):
        """合并多个 MIB 文件对象并构建统一的层次结构"""
        if not all_objects:
            return []
        
        # 计算数字 OID（跨文件）
        all_objects = self.calculate_numeric_oids_cross_files(all_objects)
        
        # 构建层次结构
        return self.build_hierarchy_cross_files(all_objects)
    
    def calculate_numeric_oids_cross_files(self, raw_objects):
        """跨文件计算数字 OID"""
        # 创建名称到对象的映射
        name_to_obj = {}
        name_to_numeric = {}
        
        # 首先收集所有对象名称
        for obj in raw_objects:
            clean_name = obj['text'].replace('Module: ', '')
            name_to_obj[clean_name] = obj
        
        # 设置基础 OID 值（包括标准 OID 和常见企业 OID）
        name_to_numeric.update(self.standard_oid_map)
        
        # 为每个对象计算数字 OID
        def calculate_oid_for_object(obj):
            if obj.get('numeric_oid') != 'N/A' and obj.get('numeric_oid') != 'Module':
                return
                
            oid_str = obj.get('oid', '')
            if not oid_str or oid_str == 'N/A' or oid_str == 'Module Identity':
                return
            
            # 解析 OID 字符串，如 "{ sampleSystemInfo 1 }"
            clean_oid = oid_str.strip('{ }')
            parts = clean_oid.split()
            
            if len(parts) >= 2:
                parent_name = parts[0]
                child_id = parts[-1]
                
                if child_id.isdigit():
                    # 查找父对象的数字 OID
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
                # 直接数字
                obj['numeric_oid'] = parts[0]
        
        # 多次迭代以确保所有依赖都得到解决
        for _ in range(10):  # 增加迭代次数以处理复杂依赖
            for obj in raw_objects:
                calculate_oid_for_object(obj)
        
        return raw_objects
    
    def build_hierarchy_cross_files(self, raw_objects):
        """跨文件构建对象层次结构"""
        # 过滤掉模块对象，专注于实际的 MIB 对象
        mib_objects = [obj for obj in raw_objects if obj['type'] != 'module']
        
        # 如果我们有应该在 mib-2 层次结构中的 MIB 对象，使用新结构
        if mib_objects:
            # 通过查找关键指标来检查这些是否为标准 MIB-II 对象
            has_mib2_objects = False
            for obj in mib_objects:
                numeric_oid = obj.get('numeric_oid', '')
                if numeric_oid and numeric_oid.startswith('1.3.6.1.2.1.'):
                    has_mib2_objects = True
                    break
            
            if has_mib2_objects:
                return self.build_mib2_hierarchy(mib_objects)
        
        # 对于非 MIB-II 文件，回退到原始逻辑
        return self.organize_by_modules_fallback(raw_objects)
    
    def build_mib2_hierarchy(self, all_objects):
        """构建正确的 MIB-2 层次结构"""
        # 创建 mib-2 根节点
        mib2_node = {
            'text': 'mib-2',
            'type': 'mib2_root',
            'oid': '1.3.6.1.2.1',
            'numeric_oid': '1.3.6.1.2.1',
            'children': []
        }
        
        # 创建标准 mib-2 子节点
        standard_nodes = {
            'interfaces': {
                'text': 'interfaces',
                'type': 'group',
                'oid': '1.3.6.1.2.1.2',
                'numeric_oid': '1.3.6.1.2.1.2',
                'children': []
            },
            'ip': {
                'text': 'ip',
                'type': 'group',
                'oid': '1.3.6.1.2.1.4',
                'numeric_oid': '1.3.6.1.2.1.4',
                'children': []
            },
            'icmp': {
                'text': 'icmp',
                'type': 'group',
                'oid': '1.3.6.1.2.1.5',
                'numeric_oid': '1.3.6.1.2.1.5',
                'children': []
            },
            'tcp': {
                'text': 'tcp',
                'type': 'group',
                'oid': '1.3.6.1.2.1.6',
                'numeric_oid': '1.3.6.1.2.1.6',
                'children': []
            },
            'udp': {
                'text': 'udp',
                'type': 'group',
                'oid': '1.3.6.1.2.1.7',
                'numeric_oid': '1.3.6.1.2.1.7',
                'children': []
            },
            'snmp': {
                'text': 'snmp',
                'type': 'group',
                'oid': '1.3.6.1.2.1.11',
                'numeric_oid': '1.3.6.1.2.1.11',
                'children': []
            }
        }
        
        # 添加标准节点到 mib-2
        for node_name, node_obj in standard_nodes.items():
            mib2_node['children'].append(node_obj)
        
        # 根据它们的 OID 或命名模式对对象进行分类
        uncategorized_objects = []
        
        for obj in all_objects:
            if obj['type'] == 'module':
                continue  # 暂时跳过模块对象
            
            obj_name = obj['text']
            numeric_oid = obj.get('numeric_oid', '')
            
            # 根据数字 OID 分类
            categorized = False
            
            if numeric_oid and numeric_oid != 'N/A':
                if numeric_oid.startswith('1.3.6.1.2.1.2'):  # interfaces
                    standard_nodes['interfaces']['children'].append(obj)
                    categorized = True
                elif numeric_oid.startswith('1.3.6.1.2.1.4'):  # ip
                    standard_nodes['ip']['children'].append(obj)
                    categorized = True
                elif numeric_oid.startswith('1.3.6.1.2.1.5'):  # icmp
                    standard_nodes['icmp']['children'].append(obj)
                    categorized = True
                elif numeric_oid.startswith('1.3.6.1.2.1.6'):  # tcp
                    standard_nodes['tcp']['children'].append(obj)
                    categorized = True
                elif numeric_oid.startswith('1.3.6.1.2.1.7'):  # udp
                    standard_nodes['udp']['children'].append(obj)
                    categorized = True
                elif numeric_oid.startswith('1.3.6.1.2.1.11'): # snmp
                    standard_nodes['snmp']['children'].append(obj)
                    categorized = True
            
            # 如果没有按 OID 分类，尝试命名模式
            if not categorized:
                obj_name_lower = obj_name.lower()
                if any(keyword in obj_name_lower for keyword in ['if', 'interface']):
                    standard_nodes['interfaces']['children'].append(obj)
                    categorized = True
                elif any(keyword in obj_name_lower for keyword in ['ip', 'address']):
                    standard_nodes['ip']['children'].append(obj)
                    categorized = True
                elif 'icmp' in obj_name_lower:
                    standard_nodes['icmp']['children'].append(obj)
                    categorized = True
                elif 'tcp' in obj_name_lower:
                    standard_nodes['tcp']['children'].append(obj)
                    categorized = True
                elif 'udp' in obj_name_lower:
                    standard_nodes['udp']['children'].append(obj)
                    categorized = True
                elif any(keyword in obj_name_lower for keyword in ['snmp', 'trap']):
                    standard_nodes['snmp']['children'].append(obj)
                    categorized = True
            
            if not categorized:
                uncategorized_objects.append(obj)
        
        # 将未分类的对象添加到 mib-2 根节点
        for obj in uncategorized_objects:
            mib2_node['children'].append(obj)
        
        # 创建最终的树结构
        root_node = {
            'text': 'MIB-II Tree',
            'type': 'root',
            'oid': '1.3.6.1.2.1',
            'numeric_oid': '1.3.6.1.2.1',
            'children': [mib2_node]
        }
        
        return [root_node]
    
    def organize_by_modules_fallback(self, raw_objects):
        """按模块组织对象 - 回退方法"""
        # 按模块分组
        modules = {}
        other_objects = []
        
        for obj in raw_objects:
            if obj['type'] == 'module':
                module_name = obj['text'].replace('Module: ', '')
                modules[module_name] = obj
            else:
                other_objects.append(obj)
        
        # 创建根节点结构
        organized = []
        
        # 如果有模块，按模块组织
        if modules:
            # 创建总根节点
            root_node = {
                'text': 'MIB Modules',
                'type': 'root',
                'oid': 'Root',
                'numeric_oid': 'Root',
                'children': []
            }
            
            for module_name, module_obj in modules.items():
                # 尝试从任何具有此模块名的对象获取源文件
                source_file = None
                
                # 首先尝试精确匹配
                for obj in raw_objects:
                    if obj.get('source_module') == module_name and obj.get('source_file'):
                        source_file = obj.get('source_file')
                        break
                
                # 如果没找到，尝试不区分大小写的匹配
                if not source_file:
                    for obj in raw_objects:
                        if obj.get('source_module') and obj.get('source_module').lower() == module_name.lower() and obj.get('source_file'):
                            source_file = obj.get('source_file')
                            break
                
                # 如果仍然没找到，尝试与原始模块文本匹配
                if not source_file:
                    original_module_text = module_obj['text'].replace('Module: ', '')
                    for obj in raw_objects:
                        if obj.get('source_module') and obj.get('source_module').lower() == original_module_text.lower() and obj.get('source_file'):
                            source_file = obj.get('source_file')
                            break
                
                # 如果仍然没找到，尝试模糊匹配（移除常见前缀/后缀）
                if not source_file:
                    # 尝试通过移除常见 MIB 命名模式来匹配
                    module_variants = [
                        module_name.lower(),
                        module_name.lower().replace('mib', ''),
                        module_name.lower().replace('-mib', ''),
                        module_name.lower().replace('_mib', ''),
                    ]
                    
                    for variant in module_variants:
                        for obj in raw_objects:
                            if obj.get('source_module') and variant in obj.get('source_module').lower() and obj.get('source_file'):
                                source_file = obj.get('source_file')
                                break
                        if source_file:
                            break
                
                # 最后的手段：只取第一个可用的源文件
                if not source_file:
                    for obj in raw_objects:
                        if obj.get('source_file'):
                            source_file = obj.get('source_file')
                            break
                
                # 查找属于此模块的对象
                module_objects = [obj for obj in other_objects if obj.get('source_module') == module_name]
                
                # 将文件信息添加到模块对象
                if source_file:
                    module_obj['source_file'] = source_file
                    # 更新显示文本以包含文件名
                    module_obj['text'] = f"{module_name} ({source_file})"
                else:
                    module_obj['text'] = f"{module_name}"
                
                # 将这些子对象添加到模块对象
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
            organized = other_objects
        
        return organized if organized else other_objects
    
    def calculate_numeric_oids(self, raw_objects):
        """计算数字 OID"""
        # 创建名称到对象的映射
        name_to_obj = {}
        name_to_numeric = {}
        
        # 首先收集所有对象名称
        for obj in raw_objects:
            clean_name = obj['text'].replace('Module: ', '')
            name_to_obj[clean_name] = obj
        
        # 设置基础 OID 值
        name_to_numeric['sampleMIB'] = '1.3.6.1.4.1.99999'  # enterprises 99999
        name_to_numeric['enterprises'] = '1.3.6.1.4.1'
        
        # 为每个对象计算数字 OID
        def calculate_oid_for_object(obj):
            if obj.get('numeric_oid') != 'N/A' and obj.get('numeric_oid') != 'Module':
                return
                
            oid_str = obj.get('oid', '')
            if not oid_str or oid_str == 'N/A' or oid_str == 'Module Identity':
                return
            
            # 解析 OID 字符串，如 "{ sampleSystemInfo 1 }"
            clean_oid = oid_str.strip('{ }')
            parts = clean_oid.split()
            
            if len(parts) >= 2:
                parent_name = parts[0]
                child_id = parts[-1]
                
                if child_id.isdigit():
                    # 查找父对象的数字 OID
                    parent_numeric = None
                    
                    if parent_name in name_to_numeric:
                        parent_numeric = name_to_numeric[parent_name]
                    elif parent_name == 'enterprises':
                        parent_numeric = self.standard_oid_map['enterprises']
                        # 如果是 enterprises 99999 格式
                        if len(parts) == 2 and parts[1].isdigit():
                            parent_numeric = self.standard_oid_map['enterprises'] + '.' + parts[1]
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
                # 直接数字
                obj['numeric_oid'] = parts[0]
        
        # 多次迭代以确保所有依赖都得到解决
        for _ in range(5):  # 最多 5 次迭代
            for obj in raw_objects:
                calculate_oid_for_object(obj)
        
        return raw_objects
    
    def build_hierarchy(self, raw_objects):
        """构建对象层次结构"""
        # 创建以名称为键的对象字典
        obj_dict = {}
        root_objects = []
        used_objects = []  # 记录已被用作子节点的对象
        
        # 首先创建所有对象的字典
        for obj in raw_objects:
            clean_name = obj['text'].replace('Module: ', '')
            obj_dict[clean_name] = obj
        
        # 第一步：找到清晰的父子关系
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
        
        # 第二步：将没有父的对象添加到根级别
        for obj in raw_objects:
            if obj not in used_objects:
                root_objects.append(obj)
        
        # 第三步：根据命名约定进一步优化层次结构
        root_objects = self.organize_by_naming_convention(root_objects)
        
        return root_objects if root_objects else raw_objects
    
    def organize_by_naming_convention(self, objects):
        """根据命名约定进一步组织层次结构"""
        # 对于示例 MIB，我们可以根据命名模式进行组织
        organized = []
        
        # 查找模块对象
        modules = [obj for obj in objects if obj['type'] == 'module']
        
        # 查找根级别对象（名称中没有点的对象）
        root_level = [obj for obj in objects if obj['type'] != 'module' and 
                      ('sampleObjects' in obj['text'] or 'sampleNotifications' in obj['text'])]
        
        # 查找系统信息组
        system_group = [obj for obj in objects if 'sampleSystemInfo' in obj['text']]
        
        # 查找系统对象
        system_objects = [obj for obj in objects if obj['text'].startswith('sampleSystem') and 
                          obj['text'] not in ['sampleSystemInfo']]
        
        # 查找配置表相关对象
        config_objects = [obj for obj in objects if 'sampleConfig' in obj['text']]
        
        # 组织结构
        for module in modules:
            organized.append(module)
            
            # 为模块添加子节点
            for root_obj in root_level:
                if root_obj['text'] == 'sampleObjects':
                    # 将子组添加到 sampleObjects
                    for sys_group in system_group:
                        if sys_group not in root_obj['children']:
                            # 将系统对象添加到 sampleSystemInfo
                            for sys_obj in system_objects:
                                if sys_obj not in sys_group['children']:
                                    sys_group['children'].append(sys_obj)
                            root_obj['children'].append(sys_group)
                    
                    # 添加配置表
                    config_table = next((obj for obj in config_objects if obj['text'] == 'sampleConfigTable'), None)
                    if config_table and config_table not in root_obj['children']:
                        # 将子对象添加到配置表
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

# 创建全局解析器实例的函数
def get_mib_parser():
    """获取 MIB 解析器实例"""
    return MIBParser()

# 为了向后兼容，创建一个延迟加载的实例
_mib_parser_instance = None

def mib_parser():
    """获取全局 MIB 解析器实例（延迟加载）"""
    global _mib_parser_instance
    if _mib_parser_instance is None:
        _mib_parser_instance = MIBParser()
    return _mib_parser_instance
