"""路由模块"""
import logging
from flask import Blueprint, render_template, request, jsonify
from file_handler import validate_and_process_files, save_uploaded_file, cleanup_file
from mib_parser import mib_parser

logger = logging.getLogger(__name__)

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """导航页面（主页）"""
    return render_template('index.html')

@main_bp.route('/mib-parser')
def mib_parser_page():
    """MIB 解析器页面"""
    return render_template('mib_parser.html')

@main_bp.route('/oid-calculator')
def oid_calculator_page():
    """SNMP命令生成器页面"""
    return render_template('oid_calculator.html')

@main_bp.route('/upload-mib', methods=['POST'])
def upload_mib():
    """处理 MIB 文件上传和解析"""
    try:
        # 检查是单文件还是多文件上传
        if 'mib_file' in request.files:
            # 单文件上传（向后兼容）
            file = request.files['mib_file']
            if file.filename == '':
                return jsonify({'success': False, 'error': '没有选择文件'})
            
            if file.filename.lower().endswith('.zip'):
                # 处理 ZIP 文件
                files_data, error = validate_and_process_files(file)
                if error:
                    return jsonify({'success': False, 'error': error})
                
                # 解析 ZIP 中的所有 MIB 文件
                result = mib_parser().parse_multiple_mib_files(files_data['files'])
                if result['success']:
                    result['zip_info'] = {
                        'filename': file.filename,
                        'extracted_files': len(files_data['files'])
                    }
                return result
            else:
                # 处理单个 MIB 文件
                file_path = save_uploaded_file(file)
                
                # 解析 MIB 文件
                result = mib_parser().parse_mib_file(file_path)
                
                # 清理临时文件
                cleanup_file(file_path)
                
                return jsonify(result)
        
        elif 'mib_files' in request.files:
            # 多文件上传
            files = request.files.getlist('mib_files')
            
            files_data, error = validate_and_process_files(files)
            if error:
                return jsonify({'success': False, 'error': error})
            
            # 解析所有 MIB 文件
            result = mib_parser().parse_multiple_mib_files(files_data['files'])
            if result['success'] and files_data['zip_info']:
                result['zip_info'] = files_data['zip_info']
            return result
        
        else:
            return jsonify({'success': False, 'error': '没有选择文件'})
            
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
