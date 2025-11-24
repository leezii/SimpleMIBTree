"""
MIB表OID生成器模块
用于根据MIB表结构和索引值生成对应的OID
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from flask import current_app

@dataclass
class TableColumn:
    """表列信息"""
    name: str
    oid: str
    description: str
    syntax: str

@dataclass
class IndexColumn:
    """索引列信息"""
    name: str
    oid: str
    type: str
    description: str

@dataclass
class MibTable:
    """MIB表信息"""
    name: str
    oid: str
    description: str
    type: str  # standard, huawei_ots, huawei_board, etc.
    columns: List[TableColumn]
    index_columns: List[IndexColumn]

class OIDGenerator:
    """OID生成器核心类"""
    
    def __init__(self, mib_manager, mib_parser):
        self.mib_manager = mib_manager
        self.mib_parser = mib_parser
        self.huawei_tables = self._load_huawei_table_configs()
        self.templates = self._load_templates()
    
    def get_device_mib_tables(self, device_id: str) -> Dict[str, Any]:
        """
        获取设备类型的所有MIB表
        
        Args:
            device_id: 设备类型ID
            
        Returns:
            包含表信息的字典
        """
        try:
            # 获取设备类型的MIB文件
            device_info = self.mib_manager.get_device_type(device_id)
            if not device_info:
                return {"success": False, "error": f"设备类型 {device_id} 不存在"}
            
            mib_files = device_info.get('mib_files', [])
            tables = []
            
            # 解析每个MIB文件，提取表信息
            for file_info in mib_files:
                file_path = file_info.get('file_path', '')
                if not file_path:
                    continue
                    
                # 设置当前文件路径，用于后续表提取
                self._current_file_path = file_path
                    
                # 解析MIB文件
                mib_data = self.mib_parser.parse_mib_file(file_path)
                if not mib_data:
                    continue
                
                # 提取表信息
                file_tables = self._extract_tables_from_mib(mib_data)
                tables.extend(file_tables)
            
            # 移除硬编码的华为设备特殊表，所有表都从MIB文件中解析
            
            table_dicts = [self._table_to_dict(table) for table in tables]
            current_app.logger.info(f"为设备 {device_id} 提取到 {len(tables)} 个表")
            for i, table in enumerate(tables[:5]):  # 只记录前5个表
                current_app.logger.info(f"表 {i+1}: {table.name} (OID: {table.oid})")
            
            return {
                "success": True,
                "data": {
                    "tables": table_dicts
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"获取设备MIB表失败: {str(e)}")
            return {"success": False, "error": f"获取MIB表失败: {str(e)}"}
    
    def generate_oid(self, device_id: str, table_name: str, index_values: List[str], 
                    selected_columns: List[str], **kwargs) -> Dict[str, Any]:
        """
        生成OID的核心方法
        
        Args:
            device_id: 设备类型ID
            table_name: 表名
            index_values: 索引值列表
            selected_columns: 选择的列名列表
            **kwargs: 其他参数（output_format, target_ip, community, snmp_version）
            
        Returns:
            生成的OID结果
        """
        try:
            # 获取表信息
            table = self._get_table_info(device_id, table_name)
            if not table:
                return {"success": False, "error": f"表 {table_name} 不存在"}
            
            # 验证索引值
            if len(index_values) != len(table.index_columns):
                return {
                    "success": False, 
                    "error": f"索引值数量不匹配，需要 {len(table.index_columns)} 个，提供了 {len(index_values)} 个"
                }
            
            # 验证列名
            valid_columns = [col.name for col in table.columns]
            invalid_columns = [col for col in selected_columns if col not in valid_columns]
            if invalid_columns:
                return {
                    "success": False,
                    "error": f"无效的列名: {', '.join(invalid_columns)}"
                }
            
            # 处理索引值
            processed_indices = self._process_index_values(index_values, table.index_columns)
            
            # 生成OID
            generated_oids = []
            for column_name in selected_columns:
                column = next((col for col in table.columns if col.name == column_name), None)
                if not column:
                    continue
                
                # 构建完整OID
                oid_parts = [table.oid, column.oid] + processed_indices
                full_oid = '.'.join(oid_parts)
                
                generated_oids.append({
                    "column_name": column_name,
                    "column_description": column.description,
                    "oid": full_oid
                })
            
            # 格式化输出
            output_format = kwargs.get('output_format', 'oid')
            formatted_results = self._format_output(generated_oids, output_format, target_ip=kwargs.get('target_ip', '192.168.1.100'), community=kwargs.get('community', 'public'), snmp_version=kwargs.get('snmp_version', '2c'))
            
            return {
                "success": True,
                "data": {
                    "generated_oids": formatted_results,
                    "table_info": self._table_to_dict(table)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"生成OID失败: {str(e)}")
            return {"success": False, "error": f"生成OID失败: {str(e)}"}
    
    def get_templates(self) -> Dict[str, Any]:
        """获取预定义模板"""
        return {
            "success": True,
            "data": {
                "templates": self.templates
            }
        }
    
    
    def _extract_tables_from_mib(self, mib_data: Dict[str, Any]) -> List[MibTable]:
        """从MIB数据中提取表信息"""
        tables = []
        
        # MIB解析器返回的数据结构可能不同，需要适配
        if isinstance(mib_data, dict):
            # 检查是否有tree结构
            if 'tree' in mib_data:
                tree_data = mib_data['tree']
                if isinstance(tree_data, list):
                    # 遍历树结构查找表
                    self._extract_tables_from_tree(tree_data, tables)
            elif 'tables' in mib_data:
                # 直接从tables字段提取
                for table_name, table_info in mib_data['tables'].items():
                    table = self._create_table_from_info(table_name, table_info, 'standard')
                    if table:
                        tables.append(table)
            
            # 尝试直接从原始MIB内容中提取表信息
            if 'module' in mib_data:
                module_name = mib_data['module']
                # 如果有文件路径，尝试直接解析文件内容
                if hasattr(self, '_current_file_path') and self._current_file_path:
                    file_tables = self._extract_tables_from_file(self._current_file_path)
                    tables.extend(file_tables)
        
        return tables
    
    def _extract_tables_from_file(self, file_path: str) -> List[MibTable]:
        """直接从MIB文件中提取表信息"""
        tables = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 使用正则表达式查找表定义
            # 修复：匹配跨行的 OBJECT-TYPE 和 SYNTAX SEQUENCE OF
            table_pattern = r'(\w+(?:-\w+)*)\s+OBJECT-TYPE[^:]*?SYNTAX\s+SEQUENCE\s+OF\s+(\w+(?:-\w+)*)'
            matches = re.findall(table_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            
            current_app.logger.info(f"在文件 {file_path} 中找到 {len(matches)} 个表定义")
            
            for table_name, entry_name in matches:
                # 查找表的OID定义
                oid_pattern = rf'{re.escape(table_name)}\s+OBJECT-TYPE[^:]*?::=\s*\{{?\s*([^}}\s]+)'
                oid_match = re.search(oid_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                
                oid = 'N/A'
                if oid_match:
                    oid = oid_match.group(1).strip()
                
                # 查找表项的列定义
                entry_pattern = rf'{re.escape(entry_name)}\s*::=\s*.*?\{{([^}}]+)\}}'
                entry_match = re.search(entry_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                
                columns = []
                if entry_match:
                    entry_content = entry_match.group(1)
                    # 提取列定义
                    column_pattern = r'(\w+(?:-\w+)*)\s+OBJECT-TYPE\s+.*?SYNTAX\s+(\w+(?:-\w+)*)'
                    column_matches = re.findall(column_pattern, entry_content, re.IGNORECASE)
                    
                    for i, (col_name, col_syntax) in enumerate(column_matches, 1):
                        column = TableColumn(
                            name=col_name,
                            oid=str(i),  # 使用序号作为OID
                            description=col_name,
                            syntax=col_syntax
                        )
                        columns.append(column)
                
                # 创建表对象
                if columns:  # 只有找到列才创建表
                    table = MibTable(
                        name=table_name,
                        oid=oid,
                        description=f"华为设备表: {table_name}",
                        type='huawei_standard',
                        columns=columns,
                        index_columns=[]  # 暂时不处理索引列
                    )
                    tables.append(table)
                    
        except Exception as e:
            current_app.logger.error(f"直接解析MIB文件表信息失败 {file_path}: {str(e)}")
        
        return tables
    
    def _extract_tables_from_tree(self, tree_nodes: List[Dict], tables: List[MibTable]):
        """从树节点中递归提取表信息"""
        for node in tree_nodes:
            # 检查是否是表节点（通常包含Table关键字）
            node_text = node.get('text', '').lower()
            if 'table' in node_text:
                # 尝试提取表信息
                table_info = self._extract_table_info_from_node(node)
                if table_info:
                    tables.append(table_info)
            
            # 递归处理子节点
            children = node.get('children', [])
            if children:
                self._extract_tables_from_tree(children, tables)
    
    def _extract_table_info_from_node(self, node: Dict) -> Optional[MibTable]:
        """从节点中提取表信息"""
        node_text = node.get('text', '')
        node_oid = node.get('numeric_oid', node.get('oid', ''))
        
        # 查找子节点中的列信息
        children = node.get('children', [])
        columns = []
        index_columns = []
        
        for child in children:
            child_text = child.get('text', '')
            child_oid = child.get('numeric_oid', child.get('oid', ''))
            
            # 判断是否是列
            if child_text and child_oid:
                # 简单的启发式：如果子节点的OID比父节点长一位，可能是列
                if node_oid and child_oid.startswith(node_oid):
                    oid_suffix = child_oid[len(node_oid):].strip('.')
                    if oid_suffix.isdigit():
                        column = TableColumn(
                            name=child_text,
                            oid=oid_suffix,
                            description=child_text,
                            syntax=child.get('syntax', 'INTEGER')
                        )
                        columns.append(column)
        
        # 如果找到了列，创建表
        if columns:
            return MibTable(
                name=node_text,
                oid=node_oid,
                description=node_text,
                type='standard',
                columns=columns,
                index_columns=index_columns
            )
        
        return None
    
    def _create_table_from_info(self, table_name: str, table_info: Dict, table_type: str) -> Optional[MibTable]:
        """从表信息创建MibTable对象"""
        try:
            # 提取列信息
            columns = []
            if 'columns' in table_info:
                for col_name, col_info in table_info['columns'].items():
                    column = TableColumn(
                        name=col_name,
                        oid=str(col_info.get('oid', '')),
                        description=col_info.get('description', col_name),
                        syntax=col_info.get('syntax', 'INTEGER')
                    )
                    columns.append(column)
            
            # 提取索引列信息
            index_columns = []
            if 'index_columns' in table_info:
                for idx_info in table_info['index_columns']:
                    index_col = IndexColumn(
                        name=idx_info.get('name', ''),
                        oid=str(idx_info.get('oid', '')),
                        type=idx_info.get('type', 'INTEGER'),
                        description=idx_info.get('description', '')
                    )
                    index_columns.append(index_col)
            
            return MibTable(
                name=table_name,
                oid=str(table_info.get('oid', '')),
                description=table_info.get('description', table_name),
                type=table_type,
                columns=columns,
                index_columns=index_columns
            )
        except Exception as e:
            current_app.logger.error(f"创建表对象失败 {table_name}: {str(e)}")
            return None
    
    
    def _get_table_info(self, device_id: str, table_name: str) -> Optional[MibTable]:
        """获取指定表的信息"""
        tables_result = self.get_device_mib_tables(device_id)
        if not tables_result['success']:
            return None
        
        for table_dict in tables_result['data']['tables']:
            if table_dict['name'] == table_name:
                return self._dict_to_table(table_dict)
        
        return None
    
    def _process_index_values(self, index_values: List[str], index_columns: List[IndexColumn]) -> List[str]:
        """处理索引值，根据类型转换格式"""
        processed = []
        
        for i, (value, index_col) in enumerate(zip(index_values, index_columns)):
            if index_col.type.lower() in ['ipaddress', 'ipaddress']:
                # IP地址格式：保持点分十进制
                processed.append(value.replace('.', '.'))
            elif index_col.type.lower() in ['integer', 'integer32', 'unsigned32']:
                # 数字类型：直接使用
                processed.append(str(int(value)))
            elif index_col.type.lower() in ['displaystring', 'octetstring']:
                # 字符串类型：转换为ASCII码
                processed.append('.'.join(str(ord(c)) for c in value))
            else:
                # 默认处理
                processed.append(str(value))
        
        return processed
    
    def _format_output(self, generated_oids: List[Dict[str, Any]], output_format: str, **kwargs) -> List[Dict[str, Any]]:
        """格式化输出结果"""
        formatted = []
        
        for oid_info in generated_oids:
            if output_format == 'oid':
                # 纯OID格式
                formatted.append({
                    "column_name": oid_info["column_name"],
                    "oid": oid_info["oid"],
                    "format": "纯OID"
                })
            elif output_format == 'snmpget':
                # SNMP命令格式
                target_ip = kwargs.get('target_ip', '192.168.1.100')
                community = kwargs.get('community', 'public')
                snmp_version = kwargs.get('snmp_version', '2c')
                
                command = f"snmpget -v{snmp_version} -c {community} {target_ip} {oid_info['oid']}"
                formatted.append({
                    "column_name": oid_info["column_name"],
                    "oid": oid_info["oid"],
                    "command": command,
                    "format": "SNMP命令"
                })
            elif output_format == 'table':
                # 表格格式
                formatted.append({
                    "column_name": oid_info["column_name"],
                    "oid": oid_info["oid"],
                    "table_format": f"{oid_info['column_name']} -> {oid_info['oid']}",
                    "format": "表格"
                })
        
        return formatted
    
    def _table_to_dict(self, table: MibTable) -> Dict[str, Any]:
        """将MibTable对象转换为字典"""
        return {
            "name": table.name,
            "oid": table.oid,
            "description": table.description,
            "type": table.type,
            "columns": [
                {
                    "name": col.name,
                    "oid": col.oid,
                    "description": col.description,
                    "syntax": col.syntax
                }
                for col in table.columns
            ],
            "index_columns": [
                {
                    "name": idx.name,
                    "oid": idx.oid,
                    "type": idx.type,
                    "description": idx.description
                }
                for idx in table.index_columns
            ]
        }
    
    def _dict_to_table(self, table_dict: Dict[str, Any]) -> MibTable:
        """将字典转换为MibTable对象"""
        columns = [
            TableColumn(
                name=col['name'],
                oid=col['oid'],
                description=col['description'],
                syntax=col['syntax']
            )
            for col in table_dict['columns']
        ]
        
        index_columns = [
            IndexColumn(
                name=idx['name'],
                oid=idx['oid'],
                type=idx['type'],
                description=idx['description']
            )
            for idx in table_dict['index_columns']
        ]
        
        return MibTable(
            name=table_dict['name'],
            oid=table_dict['oid'],
            description=table_dict['description'],
            type=table_dict['type'],
            columns=columns,
            index_columns=index_columns
        )
    
    def _load_huawei_table_configs(self) -> Dict[str, Any]:
        """加载华为设备特殊表配置 - 已弃用，所有表现在从MIB文件中解析"""
        return {}
    
    def _load_templates(self) -> Dict[str, Any]:
        """加载预定义模板"""
        return {
            "interface_basic": {
                "name": "基础接口信息",
                "description": "获取网络接口的基本信息",
                "table_type": "interface",
                "columns": ["ifDescr", "ifType", "ifAdminStatus", "ifOperStatus"],
                "output_format": "snmpget",
                "index_values": ["1"]  # 默认接口索引
            },
            "tcp_connections": {
                "name": "TCP连接状态",
                "description": "监控TCP连接状态",
                "table_type": "tcp",
                "columns": ["tcpConnState", "tcpConnLocalPort", "tcpConnRemAddress"],
                "output_format": "snmpget",
                "index_values": ["192.168.1.1", "80", "192.168.1.2", "12345"]  # 示例索引
            },
            "huawei_ots_performance": {
                "name": "华为OTS端口性能",
                "description": "获取华为设备OTS端口性能数据",
                "table_type": "huawei_ots",
                "columns": ["ots-portPer15MCurMonValue", "ots-portPer15MCurVldty"],
                "output_format": "snmpget",
                "index_values": ["1-1-1-OTS1"]  # 示例端口EID
            },
            "huawei_board_performance": {
                "name": "华为单板性能",
                "description": "获取华为设备单板性能数据",
                "table_type": "huawei_board",
                "columns": ["boardPer15MCurMonValue", "boardPer15MCurVldty"],
                "output_format": "snmpget",
                "index_values": ["1-1-1"]  # 示例单板EID
            }
        }
    
    def parse_all_device_mibs(self, device_id: str, progress_callback=None) -> Dict[str, Any]:
        """
        解析指定设备类型的所有MIB文件
        
        Args:
            device_id: 设备类型ID
            progress_callback: 进度回调函数，接收(current, total, message)参数
            
        Returns:
            包含解析结果的字典
        """
        try:
            # 获取设备类型的MIB文件
            device_info = self.mib_manager.get_device_type(device_id)
            if not device_info:
                return {"success": False, "error": f"设备类型 {device_id} 不存在"}
            
            mib_files = device_info.get('mib_files', [])
            if not mib_files:
                return {"success": False, "error": f"设备类型 {device_id} 没有MIB文件"}
            
            all_tables = []
            all_objects = []
            parsed_files = []
            failed_files = []
            
            total_files = len(mib_files)
            
            for i, file_info in enumerate(mib_files):
                if progress_callback:
                    progress_callback(i + 1, total_files, f"解析文件: {file_info.get('original_name')}")
                
                file_path = file_info.get('file_path', '')
                if not file_path or not os.path.exists(file_path):
                    failed_files.append({
                        "file_id": file_info.get("id"),
                        "filename": file_info.get("original_name"),
                        "error": "文件不存在"
                    })
                    continue
                
                try:
                    # 解析MIB文件
                    mib_data = self.mib_parser.parse_mib_file(file_path)
                    if not mib_data or not mib_data.get('success'):
                        failed_files.append({
                            "file_id": file_info.get("id"),
                            "filename": file_info.get("original_name"),
                            "error": mib_data.get('error', '解析失败') if mib_data else '解析返回空结果'
                        })
                        continue
                    
                    # 提取表信息
                    self._current_file_path = file_path
                    file_tables = self._extract_tables_from_mib(mib_data)
                    all_tables.extend(file_tables)
                    
                    # 收集所有对象用于OID映射
                    if 'tree' in mib_data:
                        self._collect_objects_from_tree(mib_data['tree'], all_objects, file_info)
                    
                    parsed_files.append({
                        "file_id": file_info.get("id"),
                        "filename": file_info.get("original_name"),
                        "tables_count": len(file_tables),
                        "objects_count": len([obj for obj in all_objects if obj.get('source_file') == file_info.get('original_name')])
                    })
                    
                except Exception as e:
                    print(f"解析文件 {file_info.get('original_name')} 失败: {str(e)}")
                    failed_files.append({
                        "file_id": file_info.get("id"),
                        "filename": file_info.get("original_name"),
                        "error": str(e)
                    })
            
            # 构建完整的OID映射
            oid_mapping = self._build_oid_mapping(all_objects)
            
            return {
                "success": True,
                "device_id": device_id,
                "parsed_files": parsed_files,
                "failed_files": failed_files,
                "total_tables": len(all_tables),
                "total_objects": len(all_objects),
                "tables": [self._table_to_dict(table) for table in all_tables],
                "oid_mapping": oid_mapping,
                "summary": {
                    "total_files": total_files,
                    "parsed_count": len(parsed_files),
                    "failed_count": len(failed_files)
                }
            }
            
        except Exception as e:
            print(f"解析设备MIB文件失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _collect_objects_from_tree(self, tree_nodes, all_objects, file_info):
        """从树节点中收集所有对象"""
        for node in tree_nodes:
            obj = {
                "text": node.get('text', ''),
                "oid": node.get('oid', ''),
                "numeric_oid": node.get('numeric_oid', ''),
                "type": node.get('type', ''),
                "source_file": file_info.get('original_name'),
                "source_file_id": file_info.get('id')
            }
            all_objects.append(obj)
            
            # 递归处理子节点
            children = node.get('children', [])
            if children:
                self._collect_objects_from_tree(children, all_objects, file_info)
    
    def _build_oid_mapping(self, all_objects):
        """构建OID映射字典"""
        oid_mapping = {}
        
        for obj in all_objects:
            numeric_oid = obj.get('numeric_oid', '')
            if numeric_oid and numeric_oid != 'N/A':
                oid_mapping[numeric_oid] = {
                    "name": obj.get('text', ''),
                    "type": obj.get('type', ''),
                    "source_file": obj.get('source_file', ''),
                    "oid": obj.get('oid', '')
                }
        
        return oid_mapping

# 全局OID生成器实例
_oid_generator = None

def get_oid_generator():
    """获取全局OID生成器实例"""
    global _oid_generator
    if _oid_generator is None:
        try:
            from .mib_manager import get_mib_manager
            from .mib_parser import get_mib_parser
        except ImportError:
            from mib_manager import get_mib_manager
            from mib_parser import get_mib_parser
        
        mib_manager = get_mib_manager()
        parser = get_mib_parser()
        _oid_generator = OIDGenerator(mib_manager, parser)
    return _oid_generator