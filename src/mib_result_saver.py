"""
MIB解析结果保存器模块
用于将解析后的MIB表和OID信息保存到设备类型目录
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MIBResultSaver:
    """MIB解析结果保存器"""
    
    def __init__(self, mib_files_dir: str = 'mib_files'):
        self.mib_files_dir = mib_files_dir
    
    def save_parsed_results(self, device_id: str, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存解析结果到设备类型目录
        
        Args:
            device_id: 设备类型ID
            parse_result: 解析结果字典
            
        Returns:
            包含保存结果的字典
        """
        try:
            if not parse_result.get('success'):
                return {"success": False, "error": "解析结果无效"}
            
            # 创建解析结果目录
            device_dir = os.path.join(self.mib_files_dir, device_id)
            parsed_results_dir = os.path.join(device_dir, 'parsed_results')
            os.makedirs(parsed_results_dir, exist_ok=True)
            
            # 准备保存数据
            timestamp = datetime.utcnow().isoformat()
            
            # 保存表信息
            tables_data = {
                "device_id": device_id,
                "parsed_at": timestamp,
                "summary": parse_result.get('summary', {}),
                "tables": parse_result.get('tables', [])
            }
            
            tables_file = os.path.join(parsed_results_dir, 'tables.json')
            with open(tables_file, 'w', encoding='utf-8') as f:
                json.dump(tables_data, f, indent=2, ensure_ascii=False)
            
            # 保存OID映射
            oid_mapping_data = {
                "device_id": device_id,
                "generated_at": timestamp,
                "summary": parse_result.get('summary', {}),
                "oid_mapping": parse_result.get('oid_mapping', {})
            }
            
            oid_mapping_file = os.path.join(parsed_results_dir, 'oid_mapping.json')
            with open(oid_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(oid_mapping_data, f, indent=2, ensure_ascii=False)
            
            # 保存完整的解析结果
            full_result_file = os.path.join(parsed_results_dir, 'full_result.json')
            with open(full_result_file, 'w', encoding='utf-8') as f:
                json.dump(parse_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"保存设备 {device_id} 的解析结果到 {parsed_results_dir}")
            
            return {
                "success": True,
                "device_id": device_id,
                "saved_files": [
                    "tables.json",
                    "oid_mapping.json", 
                    "full_result.json"
                ],
                "parsed_results_dir": parsed_results_dir
            }
            
        except Exception as e:
            logger.error(f"保存解析结果失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_parsed_results(self, device_id: str) -> Dict[str, Any]:
        """
        获取已保存的解析结果
        
        Args:
            device_id: 设备类型ID
            
        Returns:
            包含解析结果的字典
        """
        try:
            parsed_results_dir = os.path.join(self.mib_files_dir, device_id, 'parsed_results')
            
            if not os.path.exists(parsed_results_dir):
                return {"success": False, "error": "没有找到解析结果"}
            
            # 读取表信息
            tables_file = os.path.join(parsed_results_dir, 'tables.json')
            tables_data = None
            if os.path.exists(tables_file):
                with open(tables_file, 'r', encoding='utf-8') as f:
                    tables_data = json.load(f)
            
            # 读取OID映射
            oid_mapping_file = os.path.join(parsed_results_dir, 'oid_mapping.json')
            oid_mapping_data = None
            if os.path.exists(oid_mapping_file):
                with open(oid_mapping_file, 'r', encoding='utf-8') as f:
                    oid_mapping_data = json.load(f)
            
            return {
                "success": True,
                "device_id": device_id,
                "tables": tables_data,
                "oid_mapping": oid_mapping_data,
                "parsed_results_dir": parsed_results_dir
            }
            
        except Exception as e:
            logger.error(f"获取解析结果失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_parsed_results(self, device_id: str) -> Dict[str, Any]:
        """
        删除指定设备类型的解析结果
        
        Args:
            device_id: 设备类型ID
            
        Returns:
            包含删除结果的字典
        """
        try:
            parsed_results_dir = os.path.join(self.mib_files_dir, device_id, 'parsed_results')
            
            if not os.path.exists(parsed_results_dir):
                return {"success": True, "message": "没有找到解析结果目录"}
            
            # 删除目录及其内容
            import shutil
            shutil.rmtree(parsed_results_dir)
            
            logger.info(f"删除设备 {device_id} 的解析结果目录: {parsed_results_dir}")
            
            return {
                "success": True,
                "device_id": device_id,
                "message": "解析结果删除成功"
            }
            
        except Exception as e:
            logger.error(f"删除解析结果失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def list_parsed_results(self) -> Dict[str, Any]:
        """
        列出所有设备类型的解析结果
        
        Returns:
            包含所有解析结果信息的字典
        """
        try:
            if not os.path.exists(self.mib_files_dir):
                return {"success": True, "devices": []}
            
            devices = []
            
            for device_id in os.listdir(self.mib_files_dir):
                device_dir = os.path.join(self.mib_files_dir, device_id)
                if not os.path.isdir(device_dir):
                    continue
                
                parsed_results_dir = os.path.join(device_dir, 'parsed_results')
                if os.path.exists(parsed_results_dir):
                    # 检查解析结果文件
                    tables_file = os.path.join(parsed_results_dir, 'tables.json')
                    oid_mapping_file = os.path.join(parsed_results_dir, 'oid_mapping.json')
                    
                    device_info = {
                        "device_id": device_id,
                        "has_tables": os.path.exists(tables_file),
                        "has_oid_mapping": os.path.exists(oid_mapping_file),
                        "parsed_results_dir": parsed_results_dir
                    }
                    
                    # 读取解析时间
                    if os.path.exists(tables_file):
                        try:
                            with open(tables_file, 'r', encoding='utf-8') as f:
                                tables_data = json.load(f)
                                device_info["parsed_at"] = tables_data.get("parsed_at")
                                device_info["tables_count"] = len(tables_data.get("tables", []))
                        except:
                            pass
                    
                    devices.append(device_info)
            
            return {
                "success": True,
                "devices": devices
            }
            
        except Exception as e:
            logger.error(f"列出解析结果失败: {str(e)}")
            return {"success": False, "error": str(e)}

# 全局结果保存器实例
_mib_result_saver = None

def get_mib_result_saver() -> MIBResultSaver:
    """获取全局MIB结果保存器实例"""
    global _mib_result_saver
    if _mib_result_saver is None:
        _mib_result_saver = MIBResultSaver()
    return _mib_result_saver