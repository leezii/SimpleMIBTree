"""Routing module"""
import logging
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file
from file_handler import validate_and_process_files, save_uploaded_file, cleanup_file
from mib_parser import mib_parser
from mib_manager import get_mib_manager, MIBManagementError

logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Navigation page (homepage)"""
    lang = session.get('language', request.args.get('lang', 'en'))
    return render_template('index.html', lang=lang)

@main_bp.route('/mib-parser')
def mib_parser_page():
    """MIB parser page"""
    lang = session.get('language', request.args.get('lang', 'en'))
    return render_template('mib_parser.html', lang=lang)

@main_bp.route('/oid-calculator')
def oid_calculator_page():
    """SNMP command generator page"""
    lang = session.get('language', request.args.get('lang', 'en'))
    return render_template('oid_calculator.html', lang=lang)

@main_bp.route('/mib-oid-generator')
def mib_oid_generator_page():
    """MIB table OID generator page"""
    lang = session.get('language', request.args.get('lang', 'en'))
    return render_template('mib_oid_generator.html', lang=lang)

@main_bp.route('/mib-management')
def mib_management_page():
    """MIB文件管理页面"""
    lang = session.get('language', request.args.get('lang', 'en'))
    return render_template('mib_management.html', lang=lang)

@main_bp.route('/set-language')
def set_language():
    """Set language preference"""
    lang = request.args.get('lang')
    if lang in ['zh', 'en']:
        session['language'] = lang
        logger.info(f"Language set to: {lang}")
    # Redirect to previous page or homepage
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/upload-mib', methods=['POST'])
def upload_mib():
    """Handle MIB file upload and parsing"""
    try:
        # Check if single file or multi-file upload
        if 'mib_file' in request.files:
            # Single file upload (backward compatibility)
            file = request.files['mib_file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'})
            
            if file.filename.lower().endswith('.zip'):
                # Handle ZIP file
                files_data, error = validate_and_process_files(file)
                if error:
                    return jsonify({'success': False, 'error': error})
                
                # Parse all MIB files in ZIP
                result = mib_parser().parse_multiple_mib_files(files_data['files'])
                if result['success']:
                    result['zip_info'] = {
                        'filename': file.filename,
                        'extracted_files': len(files_data['files'])
                    }
                return result
            else:
                # Handle single MIB file
                file_path = save_uploaded_file(file)
                
                # Parse MIB file
                result = mib_parser().parse_mib_file(file_path)
                
                # Clean up temporary file
                cleanup_file(file_path)
                
                return jsonify(result)
        
        elif 'mib_files' in request.files:
            # Multi-file upload
            files = request.files.getlist('mib_files')
            
            files_data, error = validate_and_process_files(files)
            if error:
                return jsonify({'success': False, 'error': error})
            
            # Parse all MIB files
            result = mib_parser().parse_multiple_mib_files(files_data['files'])
            if result['success'] and files_data['zip_info']:
                result['zip_info'] = files_data['zip_info']
            return result
        
        else:
            return jsonify({'success': False, 'error': 'No file selected'})
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# MIB文件管理API端点

@main_bp.route('/api/device-types', methods=['GET'])
def get_device_types():
    """获取所有设备类型列表"""
    try:
        mib_manager = get_mib_manager()
        device_types = mib_manager.get_device_types()
        return jsonify({
            'success': True,
            'data': device_types,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"获取设备类型列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取设备类型列表失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/device-types', methods=['POST'])
def create_device_type():
    """创建新的设备类型"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据无效',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        mib_manager = get_mib_manager()
        device_type = mib_manager.create_device_type(name, description)
        
        return jsonify({
            'success': True,
            'data': device_type,
            'message': '设备类型创建成功',
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"创建设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 400
    except Exception as e:
        logger.error(f"创建设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '创建设备类型失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/device-types/<device_id>', methods=['GET'])
def get_device_type(device_id):
    """获取特定设备类型的详细信息"""
    try:
        mib_manager = get_mib_manager()
        device_type = mib_manager.get_device_type(device_id)
        return jsonify({
            'success': True,
            'data': device_type,
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"获取设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 404
    except Exception as e:
        logger.error(f"获取设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取设备类型失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/device-types/<device_id>', methods=['PUT'])
def update_device_type(device_id):
    """更新设备类型信息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据无效',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 400
        
        name = data.get('name')
        description = data.get('description')
        
        mib_manager = get_mib_manager()
        device_type = mib_manager.update_device_type(device_id, name, description)
        
        return jsonify({
            'success': True,
            'data': device_type,
            'message': '设备类型更新成功',
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"更新设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 400
    except Exception as e:
        logger.error(f"更新设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '更新设备类型失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/device-types/<device_id>', methods=['DELETE'])
def delete_device_type(device_id):
    """删除设备类型及其关联的MIB文件"""
    try:
        mib_manager = get_mib_manager()
        mib_manager.delete_device_type(device_id)
        
        return jsonify({
            'success': True,
            'message': '设备类型删除成功',
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"删除设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 400
    except Exception as e:
        logger.error(f"删除设备类型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '删除设备类型失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/device-types/<device_id>/mib-files', methods=['GET'])
def get_device_mib_files(device_id):
    """获取指定设备类型的所有MIB文件"""
    try:
        mib_manager = get_mib_manager()
        files = mib_manager.get_device_mib_files(device_id)
        return jsonify({
            'success': True,
            'data': files,
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"获取MIB文件列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 404
    except Exception as e:
        logger.error(f"获取MIB文件列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取MIB文件列表失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/mib-files/upload', methods=['POST'])
def upload_mib_file():
    """上传MIB文件并关联到设备类型"""
    try:
        # 获取表单数据
        device_id = request.form.get('device_id')
        if not device_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'DEVICE_ID_REQUIRED',
                    'message': '设备类型ID是必需的',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 400
        
        # 检查文件
        if 'mib_file' not in request.files:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FILE_REQUIRED',
                    'message': '请选择要上传的文件',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 400
        
        file = request.files['mib_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FILE_REQUIRED',
                    'message': '请选择要上传的文件',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 400
        
        # 检查是否为ZIP文件
        if file.filename.lower().endswith('.zip'):
            # 处理ZIP文件
            files_data, error = validate_and_process_files(file)
            if error:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'ZIP_PROCESSING_ERROR',
                        'message': f'ZIP文件处理失败: {error}',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }), 400
            
            # 批量上传解压后的文件
            mib_manager = get_mib_manager()
            uploaded_files = []
            
            for extracted_file in files_data['files']:
                try:
                    # 创建文件对象
                    class FileObject:
                        def __init__(self, filename, content):
                            self.filename = filename
                            self.content = content
                            self.position = 0
                        
                        def save(self, dst):
                            with open(dst, 'w', encoding='utf-8') as f:
                                f.write(self.content)
                        
                        def seek(self, position, whence=0):
                            if whence == 0:  # SEEK_SET
                                self.position = position
                            elif whence == 1:  # SEEK_CUR
                                self.position += position
                            elif whence == 2:  # SEEK_END
                                self.position = len(self.content) + position
                            return self.position
                        
                        def tell(self):
                            return self.position
                        
                        def read(self, size=-1):
                            if size == -1:
                                result = self.content[self.position:]
                                self.position = len(self.content)
                            else:
                                result = self.content[self.position:self.position+size]
                                self.position += size
                            return result
                    
                    # 提取文件名（去除路径）
                    filename_only = os.path.basename(extracted_file.filename)
                    file_obj = FileObject(filename_only, extracted_file.content)
                    file_info = mib_manager.upload_mib_file(device_id, file_obj, filename_only)
                    uploaded_files.append(file_info)
                except Exception as e:
                    logger.warning(f"上传解压文件失败 {extracted_file.filename}: {str(e)}")
                    # 继续处理其他文件
                    continue
            
            if not uploaded_files:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'NO_VALID_FILES',
                        'message': 'ZIP文件中没有有效的MIB文件',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }), 400
            
            return jsonify({
                'success': True,
                'data': uploaded_files,
                'zip_info': {
                    'filename': file.filename,
                    'extracted_files': len(files_data['files']),
                    'uploaded_files': len(uploaded_files)
                },
                'message': f'ZIP文件上传成功，共上传 {len(uploaded_files)} 个文件',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            # 处理单个MIB文件
            mib_manager = get_mib_manager()
            file_info = mib_manager.upload_mib_file(device_id, file, file.filename)
            
            return jsonify({
                'success': True,
                'data': file_info,
                'message': '文件上传成功',
                'timestamp': datetime.utcnow().isoformat()
            })
    except MIBManagementError as e:
        logger.warning(f"上传MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 400
    except Exception as e:
        logger.error(f"上传MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '上传MIB文件失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/mib-files/<file_id>', methods=['DELETE'])
def delete_mib_file(file_id):
    """删除指定的MIB文件"""
    try:
        mib_manager = get_mib_manager()
        mib_manager.delete_mib_file(file_id)
        
        return jsonify({
            'success': True,
            'message': '文件删除成功',
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"删除MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 404
    except Exception as e:
        logger.error(f"删除MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '删除MIB文件失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/mib-files/<file_id>/download', methods=['GET'])
def download_mib_file(file_id):
    """下载指定的MIB文件"""
    try:
        mib_manager = get_mib_manager()
        file_info = mib_manager.get_mib_file(file_id)
        file_path = file_info.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FILE_NOT_FOUND',
                    'message': '文件不存在',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_info.get('original_name', file_id),
            mimetype='text/plain'
        )
    except MIBManagementError as e:
        logger.warning(f"下载MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 404
    except Exception as e:
        logger.error(f"下载MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '下载MIB文件失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/mib-files/<file_id>/parse', methods=['POST'])
def parse_mib_file(file_id):
    """解析指定的MIB文件并返回结构化数据"""
    try:
        mib_manager = get_mib_manager()
        file_info = mib_manager.get_mib_file(file_id)
        file_path = file_info.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FILE_NOT_FOUND',
                    'message': '文件不存在',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 404
        
        # 使用现有的MIB解析器
        parser = mib_parser()
        result = parser.parse_mib_file(file_path)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '文件解析成功',
            'timestamp': datetime.utcnow().isoformat()
        })
    except MIBManagementError as e:
        logger.warning(f"解析MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 404
    except Exception as e:
        logger.error(f"解析MIB文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '解析MIB文件失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500

@main_bp.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取系统统计信息"""
    try:
        mib_manager = get_mib_manager()
        stats = mib_manager.get_statistics()
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取统计信息失败',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500
