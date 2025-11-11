"""文件处理模块"""
import os
import zipfile
import io
import logging
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def extract_zip_file(zip_file):
    """从 ZIP 文件中提取 MIB 文件"""
    try:
        # 读取 ZIP 文件内容到内存
        zip_content = zip_file.read()
        zip_file_obj = io.BytesIO(zip_content)
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_file_obj, 'r') as zip_ref:
            # 检查 ZIP 文件是否安全（防止路径遍历攻击）
            for file_info in zip_ref.infolist():
                filename = file_info.filename
                
                # 跳过目录和危险文件
                if filename.endswith('/') or '..' in filename or filename.startswith('/'):
                    continue
                
                # 检查文件扩展名是否为 MIB 文件
                if '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mib', 'txt', 'my'}:
                    # 提取文件内容
                    with zip_ref.open(file_info) as extracted_file:
                        file_content = extracted_file.read().decode('utf-8', errors='ignore')
                        
                        # 创建类文件对象
                        class FileLikeObject:
                            def __init__(self, filename, content):
                                self.filename = filename
                                self.content = content
                            
                            def save(self, path):
                                with open(path, 'w', encoding='utf-8') as f:
                                    f.write(self.content)
                        
                        extracted_files.append(FileLikeObject(filename, file_content))
        
        return extracted_files
        
    except zipfile.BadZipFile:
        raise Exception("无效的 ZIP 文件格式")
    except Exception as e:
        raise Exception(f"解压 ZIP 文件时出错: {str(e)}")

def validate_and_process_files(files):
    """验证并处理上传的文件"""
    if not files or (hasattr(files, '__iter__') and len(files) > 0 and files[0].filename == ''):
        return None, '没有选择文件'
    
    # 处理单个文件（向后兼容）
    if hasattr(files, 'filename'):
        files = [files]
    
    valid_files = []
    invalid_files = []
    zip_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            if file.filename.lower().endswith('.zip'):
                zip_files.append(file)
            else:
                valid_files.append(file)
        else:
            invalid_files.append(file.filename)
    
    if invalid_files:
        return None, f'无效的文件类型: {", ".join(invalid_files)}. 请上传 .mib, .txt, .my 或 .zip 文件'
    
    # 处理 ZIP 文件
    all_extracted_files = []
    zip_info = []
    
    for zip_file in zip_files:
        try:
            extracted = extract_zip_file(zip_file)
            if extracted:
                all_extracted_files.extend(extracted)
                zip_info.append({
                    'filename': zip_file.filename,
                    'extracted_files': len(extracted)
                })
        except Exception as e:
            logger.error(f"解压 ZIP 文件 {zip_file.filename} 时出错: {str(e)}")
            return None, f'解压 ZIP 文件 {zip_file.filename} 时出错: {str(e)}'
    
    # 合并所有文件
    all_files = valid_files + all_extracted_files
    
    if not all_files:
        return None, '没有有效的文件'
    
    return {
        'files': all_files,
        'zip_info': zip_info if zip_info else None
    }, None

def save_uploaded_file(file):
    """保存上传的文件并返回文件路径"""
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # 确保上传目录存在
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    file.save(file_path)
    return file_path

def cleanup_file(file_path):
    """清理临时文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"清理文件 {file_path} 时出错: {str(e)}")
