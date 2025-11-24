"""MIB文件管理器模块"""
import os
import json
import shutil
import hashlib
import time
import uuid
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class MIBManagementError(Exception):
    """MIB管理异常基类"""
    def __init__(self, code: str, message: str, details: str = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

class DeviceNotFoundError(MIBManagementError):
    """设备类型不存在异常"""
    def __init__(self, device_id: str):
        super().__init__('DEVICE_NOT_FOUND', '设备类型不存在', f'设备ID {device_id} 未找到')

class DeviceAlreadyExistsError(MIBManagementError):
    """设备类型已存在异常"""
    def __init__(self, device_name: str):
        super().__init__('DEVICE_ALREADY_EXISTS', '设备类型已存在', f'设备类型 {device_name} 已存在')

class FileNotFoundError(MIBManagementError):
    """文件不存在异常"""
    def __init__(self, file_id: str):
        super().__init__('FILE_NOT_FOUND', '文件不存在', f'文件ID {file_id} 未找到')

class InvalidFileTypeError(MIBManagementError):
    """无效文件类型异常"""
    def __init__(self, filename: str):
        super().__init__('INVALID_FILE_TYPE', '不支持的文件类型', f'文件 {filename} 不是有效的MIB文件')

class FileTooLargeError(MIBManagementError):
    """文件过大异常"""
    def __init__(self, filename: str, max_size: int):
        super().__init__('FILE_TOO_LARGE', '文件过大', f'文件 {filename} 超出最大限制 {max_size} 字节')

class StorageError(MIBManagementError):
    """存储错误异常"""
    def __init__(self, message: str):
        super().__init__('STORAGE_ERROR', '存储空间错误', message)

class MIBManager:
    """MIB文件管理器"""
    
    def __init__(self, data_dir: str = 'data', mib_files_dir: str = 'mib_files'):
        self.data_dir = data_dir
        self.mib_files_dir = mib_files_dir
        self.data_file = os.path.join(data_dir, 'mib_management.json')
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(mib_files_dir, exist_ok=True)
        
        # 初始化数据文件
        self._initialize_data_file()
    
    def _initialize_data_file(self):
        """初始化数据文件"""
        if not os.path.exists(self.data_file):
            initial_data = {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat(),
                "device_types": {},
                "settings": {
                    "max_file_size": 16 * 1024 * 1024,  # 16MB
                    "allowed_extensions": ["mib", "txt", "my", "zip"],
                    "backup_enabled": True,
                    "backup_interval": 86400,
                    "max_backups": 30
                },
                "statistics": {
                    "total_device_types": 0,
                    "total_files": 0,
                    "total_size": 0,
                    "last_backup": None
                }
            }
            self._save_data(initial_data)
            self._create_preset_device_types()
    
    def _create_preset_device_types(self):
        """创建预置设备类型"""
        preset_devices = [
            {
                "id": "dc908",
                "name": "DC 908",
                "description": "华为DC 908设备"
            },
            {
                "id": "osn1800",
                "name": "OSN 1800",
                "description": "华为OSN 1800光传输设备"
            },
            {
                "id": "osn9800",
                "name": "OSN 9800",
                "description": "华为OSN 9800光传输设备"
            }
        ]
        
        data = self._load_data()
        for device in preset_devices:
            if device["id"] not in data["device_types"]:
                device_type = {
                    "id": device["id"],
                    "name": device["name"],
                    "description": device["description"],
                    "is_preset": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "file_count": 0,
                    "total_size": 0,
                    "mib_files": []
                }
                data["device_types"][device["id"]] = device_type
                
                # 创建设备类型目录
                device_dir = os.path.join(self.mib_files_dir, device["id"])
                os.makedirs(device_dir, exist_ok=True)
        
        data["statistics"]["total_device_types"] = len(data["device_types"])
        self._save_data(data)
    
    def _load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"加载数据文件失败: {str(e)}")
            raise StorageError(f"无法加载数据文件: {str(e)}")
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据文件"""
        try:
            data["last_updated"] = datetime.utcnow().isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存数据文件失败: {str(e)}")
            raise StorageError(f"无法保存数据文件: {str(e)}")
    
    def _generate_device_type_id(self, device_name: str) -> str:
        """生成设备类型ID"""
        clean_name = re.sub(r'[^\w\s]', '', device_name.lower())
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        return clean_name
    
    def _generate_file_id(self) -> str:
        """生成文件ID"""
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        return f"file_{timestamp}_{unique_id}"
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """计算文件SHA256校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"
    
    def _validate_mib_file(self, file_path: str) -> Tuple[bool, str]:
        """验证MIB文件格式"""
        allowed_extensions = ['.mib', '.txt', '.my']
        if not any(file_path.lower().endswith(ext) for ext in allowed_extensions):
            return False, "不支持的文件类型"
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # 读取前2000字符以增加检测准确性
                mib_keywords = ['OBJECT-TYPE', 'MODULE-IDENTITY', 'OBJECT IDENTIFIER',
                               'MODULE-COMPLIANCE', 'NOTIFICATION-TYPE', 'TRAP-TYPE']
                if not any(keyword in content for keyword in mib_keywords):
                    return False, "文件内容不符合MIB格式"
        except Exception as e:
            return False, f"文件读取错误: {str(e)}"
        
        return True, "文件验证通过"
    
    def get_device_types(self) -> List[Dict[str, Any]]:
        """获取所有设备类型"""
        data = self._load_data()
        device_types = []
        
        for device_id, device_data in data["device_types"].items():
            device_types.append({
                "id": device_data["id"],
                "name": device_data["name"],
                "description": device_data["description"],
                "is_preset": device_data.get("is_preset", False),
                "created_at": device_data["created_at"],
                "updated_at": device_data["updated_at"],
                "file_count": device_data["file_count"],
                "total_size": device_data["total_size"]
            })
        
        return device_types
    
    def get_device_type(self, device_id: str) -> Dict[str, Any]:
        """获取特定设备类型"""
        data = self._load_data()
        
        if device_id not in data["device_types"]:
            raise DeviceNotFoundError(device_id)
        
        device_data = data["device_types"][device_id]
        return {
            "id": device_data["id"],
            "name": device_data["name"],
            "description": device_data["description"],
            "is_preset": device_data.get("is_preset", False),
            "created_at": device_data["created_at"],
            "updated_at": device_data["updated_at"],
            "file_count": device_data["file_count"],
            "total_size": device_data["total_size"],
            "mib_files": device_data["mib_files"]
        }
    
    def create_device_type(self, name: str, description: str = "") -> Dict[str, Any]:
        """创建新的设备类型"""
        if not name or not name.strip():
            raise MIBManagementError('DEVICE_NAME_REQUIRED', '设备类型名称不能为空')
        
        device_id = self._generate_device_type_id(name)
        data = self._load_data()
        
        # 检查ID是否已存在
        if device_id in data["device_types"]:
            raise DeviceAlreadyExistsError(name)
        
        # 检查名称是否已存在
        for existing_device in data["device_types"].values():
            if existing_device["name"].lower() == name.lower():
                raise DeviceAlreadyExistsError(name)
        
        # 创建设备类型
        now = datetime.utcnow().isoformat()
        device_type = {
            "id": device_id,
            "name": name.strip(),
            "description": description.strip(),
            "is_preset": False,
            "created_at": now,
            "updated_at": now,
            "file_count": 0,
            "total_size": 0,
            "mib_files": []
        }
        
        data["device_types"][device_id] = device_type
        data["statistics"]["total_device_types"] = len(data["device_types"])
        
        # 创建设备类型目录
        device_dir = os.path.join(self.mib_files_dir, device_id)
        os.makedirs(device_dir, exist_ok=True)
        
        self._save_data(data)
        
        logger.info(f"创建设备类型: {name} (ID: {device_id})")
        return device_type
    
    def update_device_type(self, device_id: str, name: str = None, description: str = None) -> Dict[str, Any]:
        """更新设备类型"""
        data = self._load_data()
        
        if device_id not in data["device_types"]:
            raise DeviceNotFoundError(device_id)
        
        device_data = data["device_types"][device_id]
        
        # 更新名称
        if name is not None:
            if not name or not name.strip():
                raise MIBManagementError('DEVICE_NAME_REQUIRED', '设备类型名称不能为空')
            
            new_name = name.strip()
            # 检查名称是否与其他设备冲突
            for existing_id, existing_device in data["device_types"].items():
                if existing_id != device_id and existing_device["name"].lower() == new_name.lower():
                    raise DeviceAlreadyExistsError(new_name)
            
            device_data["name"] = new_name
        
        # 更新描述
        if description is not None:
            device_data["description"] = description.strip()
        
        device_data["updated_at"] = datetime.utcnow().isoformat()
        
        self._save_data(data)
        
        logger.info(f"更新设备类型: {device_id}")
        return device_data
    
    def delete_device_type(self, device_id: str) -> bool:
        """删除设备类型"""
        data = self._load_data()
        
        if device_id not in data["device_types"]:
            raise DeviceNotFoundError(device_id)
        
        device_data = data["device_types"][device_id]
        
        # 检查是否为预置设备类型
        if device_data.get("is_preset", False):
            raise MIBManagementError('DEVICE_DELETE_FAILED', '不能删除预置设备类型')
        
        # 删除关联的文件
        for file_info in device_data["mib_files"]:
            file_path = file_info.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"删除文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {str(e)}")
        
        # 删除设备类型目录
        device_dir = os.path.join(self.mib_files_dir, device_id)
        if os.path.exists(device_dir):
            try:
                shutil.rmtree(device_dir)
                logger.info(f"删除设备目录: {device_dir}")
            except Exception as e:
                logger.warning(f"删除设备目录失败 {device_dir}: {str(e)}")
        
        # 从数据中删除
        del data["device_types"][device_id]
        data["statistics"]["total_device_types"] = len(data["device_types"])
        
        self._save_data(data)
        
        logger.info(f"删除设备类型: {device_id}")
        return True
    
    def get_device_mib_files(self, device_id: str) -> List[Dict[str, Any]]:
        """获取设备类型的MIB文件列表"""
        device_data = self.get_device_type(device_id)
        return device_data["mib_files"]
    
    def upload_mib_file(self, device_id: str, file_obj, original_filename: str) -> Dict[str, Any]:
        """上传MIB文件到指定设备类型"""
        data = self._load_data()
        
        if device_id not in data["device_types"]:
            raise DeviceNotFoundError(device_id)
        
        # 验证文件类型
        allowed_extensions = data["settings"]["allowed_extensions"]
        file_ext = os.path.splitext(original_filename)[1].lower()
        if file_ext not in [f".{ext}" for ext in allowed_extensions]:
            raise InvalidFileTypeError(original_filename)
        
        # 检查文件大小
        max_size = data["settings"]["max_file_size"]
        
        # 处理不同类型的文件对象
        if hasattr(file_obj, 'seek'):
            # 标准文件对象
            file_obj.seek(0, 2)  # 移到文件末尾
            file_size = file_obj.tell()
            file_obj.seek(0)  # 重置到开头
        else:
            # 自定义文件对象（如从ZIP解压的文件）
            file_size = len(file_obj.content) if hasattr(file_obj, 'content') else 0
        
        if file_size > max_size:
            raise FileTooLargeError(original_filename, max_size)
        
        # 生成文件ID和路径
        file_id = self._generate_file_id()
        device_dir = os.path.join(self.mib_files_dir, device_id)
        filename = f"{file_id}_{original_filename}"
        file_path = os.path.join(device_dir, filename)
        
        # 保存文件
        try:
            if hasattr(file_obj, 'save'):
                # 自定义文件对象
                file_obj.save(file_path)
            else:
                # 标准文件对象
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(file_obj, f)
        except Exception as e:
            raise StorageError(f"文件保存失败: {str(e)}")
        
        # 验证MIB文件（跳过ZIP文件验证）
        if file_ext != '.zip':
            is_valid, validation_msg = self._validate_mib_file(file_path)
            if not is_valid:
                # 删除无效文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise InvalidFileTypeError(f"{original_filename}: {validation_msg}")
        
        # 计算校验和
        checksum = self._calculate_file_checksum(file_path)
        
        # 创建文件信息
        now = datetime.utcnow().isoformat()
        file_info = {
            "id": file_id,
            "filename": filename,
            "original_name": original_filename,
            "file_path": file_path,
            "relative_path": os.path.join(device_id, filename),
            "file_size": file_size,
            "checksum": checksum,
            "upload_time": now,
            "last_modified": now,
            "mime_type": "application/zip" if file_ext == '.zip' else "text/plain",
            "encoding": "utf-8"
        }
        
        # 更新设备类型数据
        device_data = data["device_types"][device_id]
        device_data["mib_files"].append(file_info)
        device_data["file_count"] = len(device_data["mib_files"])
        device_data["total_size"] += file_size
        device_data["updated_at"] = now
        
        # 更新统计信息
        data["statistics"]["total_files"] += 1
        data["statistics"]["total_size"] += file_size
        
        self._save_data(data)
        
        logger.info(f"上传MIB文件: {original_filename} 到设备类型 {device_id}")
        return file_info
    
    def delete_mib_file(self, file_id: str) -> bool:
        """删除MIB文件"""
        data = self._load_data()
        
        # 查找文件
        file_found = False
        device_id = None
        file_info = None
        
        for dev_id, device_data in data["device_types"].items():
            for i, file in enumerate(device_data["mib_files"]):
                if file["id"] == file_id:
                    file_found = True
                    device_id = dev_id
                    file_info = file
                    break
            if file_found:
                break
        
        if not file_found:
            raise FileNotFoundError(file_id)
        
        # 删除物理文件
        file_path = file_info.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"删除文件: {file_path}")
            except Exception as e:
                logger.warning(f"删除文件失败 {file_path}: {str(e)}")
        
        # 从数据中删除
        device_data = data["device_types"][device_id]
        device_data["mib_files"] = [f for f in device_data["mib_files"] if f["id"] != file_id]
        device_data["file_count"] = len(device_data["mib_files"])
        device_data["total_size"] -= file_info["file_size"]
        device_data["updated_at"] = datetime.utcnow().isoformat()
        
        # 更新统计信息
        data["statistics"]["total_files"] -= 1
        data["statistics"]["total_size"] -= file_info["file_size"]
        
        self._save_data(data)
        
        logger.info(f"删除MIB文件: {file_id}")
        return True
    
    def get_mib_file(self, file_id: str) -> Dict[str, Any]:
        """获取MIB文件信息"""
        data = self._load_data()
        
        for device_data in data["device_types"].values():
            for file_info in device_data["mib_files"]:
                if file_info["id"] == file_id:
                    return file_info
        
        raise FileNotFoundError(file_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        data = self._load_data()
        return data["statistics"]
    
    def backup_data(self) -> str:
        """备份数据"""
        backup_dir = os.path.join("backups", "mib_management")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mib_management_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(self.data_file, backup_path)
            
            # 清理旧备份
            self._cleanup_old_backups(backup_dir)
            
            # 更新最后备份时间
            data = self._load_data()
            data["statistics"]["last_backup"] = datetime.utcnow().isoformat()
            self._save_data(data)
            
            logger.info(f"数据备份完成: {backup_path}")
            return backup_path
        except Exception as e:
            raise StorageError(f"备份失败: {str(e)}")
    
    def _cleanup_old_backups(self, backup_dir: str, max_backups: int = 30):
        """清理旧备份文件"""
        try:
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
            backup_files.sort(reverse=True)
            
            for backup_file in backup_files[max_backups:]:
                os.remove(os.path.join(backup_dir, backup_file))
                logger.info(f"删除旧备份: {backup_file}")
        except Exception as e:
            logger.warning(f"清理备份文件失败: {str(e)}")
    
    def cleanup_missing_files(self) -> Dict[str, Any]:
        """
        清理数据库中不存在于文件系统中的MIB文件记录
        
        Returns:
            Dict包含清理结果统计信息
        """
        try:
            data = self._load_data()
            cleaned_files = []
            total_files_before = 0
            total_files_after = 0
            
            for device_id, device_data in data["device_types"].items():
                mib_files = device_data.get("mib_files", [])
                total_files_before += len(mib_files)
                
                # 过滤出实际存在的文件
                valid_files = []
                for file_info in mib_files:
                    file_path = file_info.get("file_path", "")
                    if file_path and os.path.exists(file_path):
                        valid_files.append(file_info)
                    else:
                        cleaned_files.append({
                            "device_id": device_id,
                            "file_id": file_info.get("id"),
                            "filename": file_info.get("filename"),
                            "file_path": file_path
                        })
                        logger.warning(f"清理不存在的文件记录: {file_path}")
                
                # 更新设备数据
                device_data["mib_files"] = valid_files
                device_data["file_count"] = len(valid_files)
                device_data["total_size"] = sum(f.get("file_size", 0) for f in valid_files)
                device_data["updated_at"] = datetime.utcnow().isoformat()
                total_files_after += len(valid_files)
            
            # 更新统计信息
            data["statistics"]["total_files"] = total_files_after
            data["statistics"]["total_size"] = sum(
                device_data.get("total_size", 0)
                for device_data in data["device_types"].values()
            )
            data["last_updated"] = datetime.utcnow().isoformat()
            
            self._save_data(data)
            
            logger.info(f"清理完成: 删除了 {len(cleaned_files)} 个不存在的文件记录")
            
            return {
                "success": True,
                "cleaned_count": len(cleaned_files),
                "cleaned_files": cleaned_files,
                "total_files_before": total_files_before,
                "total_files_after": total_files_after
            }
            
        except Exception as e:
            logger.error(f"清理不存在文件失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# 全局MIB管理器实例
_mib_manager = None

def get_mib_manager() -> MIBManager:
    """获取全局MIB管理器实例"""
    global _mib_manager
    if _mib_manager is None:
        _mib_manager = MIBManager()
    return _mib_manager